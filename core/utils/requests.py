import aiohttp

from handlers.constants import (
    API_URL_V1, API_URL_V2, API_KEY, BASKET, SEARCH_NAME, PHOTO_URL,
    MARKUP_URL, OUTLETS)


async def get_request(add_url: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL_V1}{add_url}"
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            response_data = data['response']
            return response_data


async def get_outlets_info():
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL_V2 + OUTLETS}"
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def request_search_name(name: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL_V1 + SEARCH_NAME}?q={name}&a=1"
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def request_basket_delete():
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        url = f"{API_URL_V1 + BASKET}"
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


async def set_markup_request(markup: float):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': API_KEY,
        }
        data = {
            "markup": markup
        }
        url = f"{API_URL_V1 + MARKUP_URL}"
        async with session.patch(url, headers=headers, data=data) as response:
            return await response.json()
