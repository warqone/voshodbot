import aiohttp

from handlers.constants import API_URL, API_KEY, BASKET, SEARCH_NAME, PHOTO_URL


async def get_request(add_url: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL}{add_url}"
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            response_data = data['response']
            return response_data


async def request_search_name(name: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL + SEARCH_NAME}?q={name}&a=1"
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def request_basket_delete():
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL + BASKET}"
        async with session.delete(url, headers=headers) as response:
            return await response.json()


async def get_product_photo(detail: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{PHOTO_URL + detail}"
        async with session.get(url, headers=headers) as response:
            return await response
