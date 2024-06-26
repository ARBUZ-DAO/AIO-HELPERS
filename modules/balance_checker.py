import csv
from data.config import ERC20_ABI
from settings import Value_EVM_Balance_Checker
from loguru import logger
from data.data import DATA
import aiohttp
import asyncio
from modules.utils.multicall import Multicall
from modules.utils.helpers import round_to
from termcolor import cprint
from tabulate import tabulate
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth


class BalanceChecker:
    def __init__(self, wallets):
        self.wallets = wallets

    def get_web3(self, chain):
        return Web3(AsyncHTTPProvider(DATA[chain]['rpc']), modules={"eth": (AsyncEth)}, middlewares=[])

    async def get_prices(self):
        self.prices = {}
        for chain, coins in Value_EVM_Balance_Checker.evm_tokens.items():
            web3 = self.get_web3(chain)
            for address_contract in coins:
                if address_contract == '':  # eth
                    symbol = DATA[chain]['token']
                else:
                    token_contract = web3.eth.contract(address=web3.to_checksum_address(address_contract),
                                                       abi=ERC20_ABI)
                    symbol = await token_contract.functions.symbol().call()

                self.prices.update({symbol: 0})

        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in self.prices:
                if symbol == 'CORE':
                    url = f'https://min-api.cryptocompare.com/data/price?fsym=COREDAO&tsyms=USDT'
                else:
                    url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'

                tasks.append(self.fetch_price(session, symbol, url))

            await asyncio.gather(*tasks)

        logger.success('got prices')

    async def fetch_price(self, session, symbol, url):
        try:
            async with session.get(url) as response:
                result = await response.json()
                price = result['USDT']
                self.prices[symbol] = float(price)
        except Exception as error:
            logger.error(f'{symbol}: error. Set price: 0')
            self.prices[symbol] = 0

    async def get_tokens_data(self):
        list_decimals = {}
        list_symbols = {}

        for chain, coins in Value_EVM_Balance_Checker.evm_tokens.items():
            web3 = self.get_web3(chain)
            list_decimals[chain] = {}
            list_symbols[chain] = {}
            for coin in coins:
                if coin != '':  # != NATIVE TOKEN
                    coin = web3.to_checksum_address(coin)
                    token_contract = web3.eth.contract(address=coin, abi=ERC20_ABI)
                    decimals = await token_contract.functions.decimals().call()
                    symbol = await token_contract.functions.symbol().call()
                    list_decimals[chain][coin] = decimals
                    list_symbols[chain][coin] = symbol

        return list_decimals, list_symbols

    def transform_dict(self, input_dict):
        result = {}
        for chain, wallets in input_dict.items():
            for wallet, tokens in wallets.items():
                if wallet not in result:
                    result[wallet] = {}
                result[wallet][chain] = tokens

        return result

    async def evm_balances(self):
        erc20_coins = {chain: [] for chain in Value_EVM_Balance_Checker.evm_tokens}
        decimals_list, symbols_list = await self.get_tokens_data()
        tasks = [Multicall(chain).get_balances(self.wallets, tokens, symbols_list, decimals_list) for chain, tokens in Value_EVM_Balance_Checker.evm_tokens.items() if tokens]
        results = await asyncio.gather(*tasks)
        result = {chain: result for chain, result in zip(erc20_coins.keys(), results)}
        result = self.transform_dict(result)
        return result

    def send_result(self, result):
        small_wallets, small_wallets_value, balances, headers, send_table, total_value = [], [], {}, [[
            'number', 'wallet', '$value'], [], ['TOTAL_AMOUNTS', '', ''], ['TOTAL_VALUE', '']], [], []

        for number, (wallet, chains) in enumerate(result.items(), start=1):
            h_ = [number, wallet]
            wallet_value = 0

            for chain, coins in chains.items():
                for coin, balance in coins.items():
                    balance = round_to(balance)
                    symbol = coin.split('-')[0]
                    price = self.prices.get(symbol, 1)
                    value = int(balance * price)
                    wallet_value += value

                    head = f'{coin}-{chain.lower()}'

                    if head not in headers[0]:
                        headers[0].append(head)

                    h_.append(balance)

                    balances.setdefault(head, 0)
                    balances[head] += balance

                    if (
                            chain.lower() == Value_EVM_Balance_Checker.min_token_balance['chain'].lower() and
                            coin.lower() == Value_EVM_Balance_Checker.min_token_balance['coin'].lower() and
                            balance < Value_EVM_Balance_Checker.min_token_balance['amount']
                    ):
                        small_wallets.append(wallet)

            h_.insert(2, wallet_value)
            headers[1].append(h_)

            if wallet_value < Value_EVM_Balance_Checker.min_value_balance:
                small_wallets_value.append(wallet)

        for coin, balance in balances.items():
            balance = round_to(balance)
            symbol = coin.split('-')[0]
            price = self.prices.get(symbol, 1)
            value = int(balance * price)
            total_value.append(value)
            send_table.append([coin, balance, f'{value} $'])
            headers[2].append(round_to(balance))  # Record the total_amounts of each coin

        tokens = self.generate_csv(headers, send_table, total_value, small_wallets, small_wallets_value)

        cprint(f'\nAll balances :\n', 'blue')
        cprint(tokens, 'white')
        cprint(f'\nTOTAL_VALUE : {int(sum(total_value))} $', 'blue')
        cprint(f'\nResults written to file: results/balances.csv\n', 'blue')

    def generate_csv(self, headers, send_table, total_value, small_wallets, small_wallets_value):
        with open(f'results/balances.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(headers[0])
            spamwriter.writerows(headers[1])

            # send_table = [[coin, balance, f'{value} $'] for coin, balance, value in send_table]
            total_value = [str(value) for value in total_value]

            headers[3].insert(2, f'{int(sum(map(int, total_value)))} $')

            spamwriter.writerow([])
            spamwriter.writerows(headers[2:])

            spamwriter.writerow([])
            self.print_wallets(spamwriter, small_wallets, 'amount')
            spamwriter.writerow([])
            self.print_wallets(spamwriter, small_wallets_value, 'value')

            table_type = 'double_grid'
            head_table = ['token', 'amount', 'value']
            tokens = tabulate(send_table, head_table, tablefmt=table_type)

            return tokens

    def print_wallets(self, spamwriter, wallets, _type):
        if wallets:
            if _type == 'amount':
                small_text = f'{Value_EVM_Balance_Checker.min_token_balance["coin"]} [{Value_EVM_Balance_Checker.min_token_balance["chain"]}] balance on these wallets < {Value_EVM_Balance_Checker.min_token_balance["amount"]} :'
                spamwriter.writerow([small_text])
            elif _type == 'value':
                small_text = f'Value balance on these wallets < ${Value_EVM_Balance_Checker.min_value_balance} :'
                spamwriter.writerow([small_text])

            cprint(f'\n{small_text}', 'blue')
            for number, wallet in enumerate(wallets, start=1):
                cprint(wallet, 'white')
                spamwriter.writerow([number, wallet])

    async def start(self):
        await self.get_prices()
        evm_balances = await self.evm_balances()
        self.send_result(evm_balances)
