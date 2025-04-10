from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

from utils.db import get_user_token


class UserTokenMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        user_id = data.get("event_from_user", {}).id

        if user_id:
            user_token = await get_user_token(user_id)
            data["user_api_token"] = user_token

        return await handler(event, data)
