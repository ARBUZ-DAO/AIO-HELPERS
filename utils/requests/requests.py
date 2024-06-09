import aiohttp
from utils.requests import exceptions


async def async_get(url: str, headers: dict | None = None, **kwargs) -> dict | None:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url, **kwargs) as response:
            status_code = response.status
            response = await response.json()
            if status_code <= 201:
                return response

            raise exceptions.HTTPException(response=response, status_code=status_code)