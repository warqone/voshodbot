import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from handlers.start import start_router
from settings import ADMIN_ID, BOT_TOKEN


async def on_startup(bot: Bot):
    await bot.send_message(ADMIN_ID, text='Бот запущен.')


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    await bot.send_message(ADMIN_ID, text='Бот остановлен.')
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()


async def start():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    logger = logging.getLogger(__name__)
    asyncio.run(start())
