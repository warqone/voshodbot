from http import HTTPStatus
import logging

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message, FSInputFile
import requests

from handlers.constants import API_URL_V1, ORDERS
from keyboards import start_kb
from utils.db import add_or_update_user, check_user_token
from utils.utils import load_file

main_menu_link = load_file('/data/main_menu_link.txt')
instruction_txt = load_file('/data/instruction.txt')
logger = logging.getLogger(__name__)

start_router = Router()


class TokenForm(StatesGroup):
    add_token = State()


@start_router.message(Command(commands='start'))
async def get_start(message: Message, state: FSMContext):
    await state.clear()
    user = await check_user_token(message.from_user.id)
    if user:
        await message.answer(
            '<b>У вас уже добавлен ключ API.</b>\n'
            'Хотите его изменить?',
            reply_markup=start_kb.change_token_button()
        )
    else:
        await message.answer(
            f'<b>Привет, {message.from_user.first_name}!\n'
            'Добро пожаловать в наш бот!</b>\n' + instruction_txt,
            reply_markup=start_kb.token_link_button()
        )
        await state.set_state(TokenForm.add_token)


@start_router.callback_query(F.data.in_(['change_token', 'approve_token']))
async def change_token(call: CallbackQuery, bot: Bot, state: FSMContext):
    select = call.data
    if select == 'change_token':
        await call.message.edit_text(
            instruction_txt,
            reply_markup=start_kb.token_link_button()
        )
        await state.set_state(TokenForm.add_token)
    elif select == 'approve_token':
        await call.message.delete()
        await get_main_menu(call.from_user.id, bot)


@start_router.message(StateFilter(TokenForm.add_token))
async def get_user_token(message: Message, state: FSMContext, bot: Bot):
    await message.answer('Проверка ключа API..')
    api_token = message.text
    try:
        headers = {
            'X-Voshod-API-KEY': api_token
        }
        response = requests.get(f'{API_URL_V1 + ORDERS}', headers=headers)
        if response.status_code == HTTPStatus.OK:
            await message.answer('Ключ API добавлен успешно.')
            await add_or_update_user(
                message.from_user.id,
                message.from_user.username,
                api_token
            )
            await state.clear()
            await get_main_menu(message.from_user.id, bot)
        else:
            await message.answer_photo(
                FSInputFile('/data/token.png'),
                caption=(
                    '<b>Неверный ключ API.</b>\n'
                    'Скопируйте целиком выделенный красным текст и '
                    'вставьте в поле ввода.')
            )
    except Exception as e:
        logger.error(f'Ошибка при попытке добавить токен: {e}')
        await message.answer(
            'Произошла неизвестная ошибка. Попробуйте позже.')


@start_router.message(Command(commands='main'))
async def command_main_menu(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user = await check_user_token(message.from_user.id)
    if user:
        await get_main_menu(message.from_user.id, bot)
    else:
        await message.answer(
            '<b>Вы не добавили ключ API.</b>\n' + instruction_txt,
            reply_markup=start_kb.token_link_button()
        )
        await state.set_state(TokenForm.add_token)


@start_router.callback_query(F.data == 'back_to_main')
async def get_main_menu(user_id: int, bot: Bot):
    await bot.send_message(
        chat_id=user_id,
        text=('<b>Добро пожаловать в наш бот!\n'
              'Выберите действие из меню:</b>'),
        reply_markup=start_kb.main_menu_buttons()
    )


async def send_main_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        '<b>Выберите действие из меню:</b>',
        reply_markup=start_kb.main_menu_buttons()
    )
