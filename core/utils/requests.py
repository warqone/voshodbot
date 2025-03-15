import requests

from handlers.constants import API_URL, SEARCH_NAME

async def request_search_name(name: str):
    try:
        await requests.get()