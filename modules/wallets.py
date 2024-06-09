from better_web3 import Wallet
import csv
from loguru import logger


class Wallets:
    @staticmethod
    def generate_wallets(amount: int):
        file_path = 'results/wallets.csv'
        with open(file_path, 'w', newline='') as csvfile:
            table_head = ['number', 'address', 'privet_key']
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(table_head)

            for number in range(amount):
                wallet = Wallet.generate()

                spamwriter.writerow([number + 1, wallet.address, wallet.private_key])

        logger.success('Все кошельки сгенерированы и записаны в файл results/wallets_section.txt')

    @staticmethod
    def addresses_from_private_keys(private_keys: list):
        if len(private_keys) > 0:
            file_path = 'results/addresses.csv'
            with open(file_path, 'w', newline='') as csvfile:
                table_head = ['number', 'address', 'privet_key']
                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(table_head)

                for number, private_key in enumerate(private_keys):
                    wallet = Wallet.from_key(private_key)

                    spamwriter.writerow([number + 1, wallet.address, wallet.private_key])

            logger.success('Все адреса получены и записаны в файл results/addresses.txt')

        else:
            logger.error('В файле inputs/private_keys.txt нет приватных ключей')
