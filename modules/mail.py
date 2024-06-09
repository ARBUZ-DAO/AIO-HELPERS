from utils.requests import requests


class Mail:
    def __init__(self):
        self.base_url = 'https://www.1secmail.com/api/v1/'

    async def generate_mail(self, amount=1):
        response = await requests.async_get(url=f'{self.base_url}/?action=genRandomMailbox&count={amount}')
        return response
