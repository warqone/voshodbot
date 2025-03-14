from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

start_router = Router()


@start_router.message(F.text == "/start", Command(commands='start'))
async def get_start(message: Message):
    await message.answer(
        f'<b>Привет, {message.from_user.first_name}!\n'
        'Добро пожаловать в наш бот! Для продолжения работы, необходимо '
        'выполнить следующие шаги:</b>\n'
        '1️⃣ Нажав на кнопку, перейти на наш сайт\n'
        '2️⃣ Создать, либо скопировать ключ API\n'
        '3️⃣ Вставить ключ API в поле ниже\n'
        '4️⃣ Отправить сообщение с ключом API.'
    )
