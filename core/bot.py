import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import (SimpleRequestHandler,
                                            setup_application)
from aiohttp import web

import settings
from handlers.start import start_router, send_main_menu
from handlers.search_name import search_name_router
from handlers.search_cross import search_cross_router
from handlers.basket import basket_router
from handlers.cabinet import cabinet_router
from handlers.info import info_router
from middlewares.token import UserTokenMiddleware
from utils.db import create_users_db


async def on_startup(bot: Bot):
    await bot.set_webhook(f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}")
    await bot.send_message(settings.ADMIN_ID, text='Бот запущен.')


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    await bot.send_message(settings.ADMIN_ID, text='Бот остановлен.')
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()


async def start():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    dp = Dispatcher()
    dp.update.middleware(UserTokenMiddleware())
    dp.include_router(start_router)
    dp.include_router(search_name_router)
    dp.include_router(search_cross_router)
    dp.include_router(basket_router)
    dp.include_router(cabinet_router)
    dp.include_router(info_router)
    dp.callback_query.register(send_main_menu, F.data == 'back_to_main')
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await create_users_db()
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        host=settings.WEB_SERVER_HOST,
        port=settings.WEB_SERVER_PORT)
    await site.start()

    await asyncio.Event().wait()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    logger = logging.getLogger(__name__)
    asyncio.run(start())
