from better_web3 import Wallet
import csv
from loguru import logger


def generate_wallets(amount: int):
    file_path = 'results/wallets.csv'
    with open(file_path, 'w', newline='') as csvfile:
        table_head = ['number', 'address', 'privet_key']
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(table_head)

        for number in range(amount):
            wallet = Wallet.generate()

            spamwriter.writerow([number + 1, wallet.address, wallet.private_key])

    logger.success('Все кошельки сгенерированы и записаны в файл results/wallets.txt')
