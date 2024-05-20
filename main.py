import asyncio
import modules


async def main():
    user_action: int = int(input('\n1) Генерация EVM кошельков'
                                 '\nВыберите модуль: '))

    if user_action == 1:
        amount: int = int(input('Сколько кошельков сгенерировать: '))
        modules.generate_wallets(amount)


if __name__ == '__main__':
    asyncio.run(main())
