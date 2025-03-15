import logging

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.start_kb import back_to_main_menu_button
from utils.requests import request_search_name

search_name_router = Router()
logger = logging.getLogger(__name__)


class SearchForm(StatesGroup):
    get_name = State()


@search_name_router.callback_query(F.data == 'search_name')
async def search_name(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        '<b>Для поиска по наименованию введите название запчасти.</b>\n'
        '<i>Пример: \n- масляный фильтр VW Polo\n- воздушный фильтр vesta</i>',
        reply_markup=back_to_main_menu_button()
    )
    await state.set_state(SearchForm.get_name)


@search_name_router.message(StateFilter(SearchForm.get_name))
async def get_search_name(message: Message, bot: Bot, state: FSMContext):
    name = message.text
    if len(name) < 3:
        await message.answer(
            '<b>Слишком короткое название запчасти.</b>')
        return
    try:
        await message.answer(
            f'<b>Поиск запчастей по наименованию: {message.text}...</b>')
        data = await request_search_name(message.text)
        if data and 'response' in data and 'items' in data['response']:
            products = data['response']['items']
            await send_product_list(
                message, products, bot, state)
        else:
            await message.reply(
                '<b>Товары не найдены. Попробуйте другое.</b>',
                reply_markup=back_to_main_menu_button())
    except Exception as e:
        logger.error(
            f'Произошла ошибка при поиске запчастей по наименованию: {e}')
        await message.answer(
            '<b>Произошла неизвестная ошибка. Скоро поправим!</b>',
            reply_markup=back_to_main_menu_button())


async def send_product_list(
        message: Message,
        products: list, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await state.update_data(products=products)
    current_page = data.get("current_page", 0)
    start_index = current_page * 5
    end_index = start_index + 5
    products_to_show = products[start_index:end_index]
    message_text = f'<b>Найденные товары:</b>\nСтраница {current_page + 1}\n\n'
    kb = InlineKeyboardBuilder()
    for product in products_to_show:
        name = product['name']
        oem_brand = product['oem_brand']
        oem_num = product['oem_num']
        price = product['price']
        count = product['count']
        unit = product['unit']

        message_text += (
            f'<b>{name}\nПроизводитель:</b> {oem_brand}\n'
            f'<b>Артикул:</b> {oem_num}\n<b>Цена:</b> {price} руб.\n'
            f'<b>Количество на складах:</b> {count} {unit}\n\n'
        )
        kb.button(text=f'{oem_num} ({price} руб.)',
                  callback_data=f'detail_{product["mog"]}')
    if current_page > 0:
        kb.button(text='⬅️ Назад', callback_data='prev_page')
    if end_index < len(products):
        kb.button(text='Вперёд ➡️', callback_data='next_page')
    kb.adjust(1)

    await message.edit_text(message_text, reply_markup=kb.as_markup())


@search_name_router.callback_query(F.data.in_(['prev_page', 'next_page']))
async def handle_pagination(call: CallbackQuery, state: FSMContext):
    """
    Обрабатывает пагинацию (кнопки "Назад" и "Вперёд").
    """
    data = await state.get_data()
    products = data.get("products", [])
    current_page = data.get("current_page", 0)

    if call.data == "prev_page" and current_page > 0:
        current_page -= 1
    elif call.data == "next_page":
        current_page += 1

    await state.update_data(current_page=current_page)
    await send_product_list(call.from_user.id, products, call.bot, state)
