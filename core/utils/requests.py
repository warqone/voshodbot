import aiohttp
import json

from handlers.constants import (
    API_URL_V1, API_URL_V2, BASKET, SEARCH_NAME, SEARCH_CROSS, PHOTO_URL,
    MARKUP_URL, OUTLETS, ORDERS)


async def get_request(add_url: str, user_api_token: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        url = f"{API_URL_V1}{add_url}"
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            response_data = data['response']
            return response_data


async def get_outlets_info(user_api_token: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        url = f"{API_URL_V2 + OUTLETS}"
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def request_search_name(name: str, user_api_token: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        url = f"{API_URL_V1 + SEARCH_NAME}?q={name}&a=1"
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def request_search_cross(query: str, user_api_token: str, brand=None):
    """Выполняет запрос к API для поиска по кросс-номеру."""
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        if brand:
            query = f"{query},{brand}"
        url = f"{API_URL_V1 + SEARCH_CROSS}?q={query}&a=1"
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data['response']


async def get_orders_info(user_api_token: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        url = f"{API_URL_V2 + ORDERS}"
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def request_add_to_basket(product_id: str,
                                user_api_token: str,
                                quantity: int = 1):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        data = {
            "items": [
                {
                    "mog": product_id,
                    "count": quantity
                    }
            ]
        }
        url = f"{API_URL_V1 + BASKET}"
        async with session.patch(
                url, headers=headers, data=json.dumps(data)) as response:
            return await response.json()


async def request_basket_delete(user_api_token: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        url = f"{API_URL_V1 + BASKET}"
        async with session.delete(url, headers=headers) as response:
            return await response.json()


async def get_product_photo(detail: str, user_api_token: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        url = f"{PHOTO_URL + detail}"
        async with session.get(url, headers=headers) as response:
            return await response


async def set_markup_request(markup: float, user_api_token: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        data = {
            "markup": markup
        }
        url = f"{API_URL_V1 + MARKUP_URL}"
        async with session.patch(
                url, headers=headers, data=json.dumps(data)) as response:
            return await response.json()


async def create_order(user_api_token: str, outlet_id: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            'X-Voshod-API-KEY': user_api_token,
        }
        data = {
            "order": {
                "delivery_type": 1,
                "delivery_address": outlet_id
            }
        }
        url = f"{API_URL_V1 + BASKET}"
        async with session.post(
                url,
                headers=headers,
                data=json.dumps(data)) as response:
            return await response.json()
