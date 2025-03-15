import aiohttp

from handlers.constants import API_URL, SEARCH_NAME


async def request_search_name(name: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL + SEARCH_NAME}?q={name}&a=1"
        async with session.get(url, headers=headers) as response:
            return await response.json()
