import asyncio
from modules import Wallets, BalanceChecker
from utils import files
from utils.files import read_txt


async def main():
    section: int = int(input('\n1) Кошельки'
                             '\n2) Balance checker (настройка в settings.py)'
                             '\nВыберите раздел: '))

    # Кошельки
    if section == 1:
        user_action: int = int(input('\n1) Генерация кошельков EVM'
                                     '\n2) Получение адресов из приватных ключей EVM (заполните inputs/private_keys.txt)'
                                     '\nВыберите модуль: '))

        if user_action == 1:
            amount: int = int(input('Сколько кошельков сгенерировать: '))
            Wallets().generate_wallets(amount)

        if user_action == 2:
            private_keys = files.read_txt('input/private_keys.txt')
            Wallets().addresses_from_private_keys(private_keys)

    if section == 2:
        await BalanceChecker(read_txt('input/addresses.txt')).start()

if __name__ == '__main__':
    asyncio.run(main())
