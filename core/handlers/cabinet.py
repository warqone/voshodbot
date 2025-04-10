from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.cabinet_kb import (
    cabinet_keyboard, back_to_cabinet_keyboard, set_orders_list_keyboard)
from handlers.constants import ORDERS, MARKUP_URL
from handlers.start import send_main_menu
from utils.requests import get_request, get_outlets_info, set_markup_request

cabinet_router = Router()


class Markup(StatesGroup):
    wait_for_markup = State()


@cabinet_router.callback_query(F.data == "account")
async def account_info(call: CallbackQuery, state: FSMContext):
    await state.clear()
    data = await get_request(MARKUP_URL)
    await call.message.edit_text(
        f'<b>Установленная наценка на товары:</b> {data["markup"]}%',
        reply_markup=cabinet_keyboard()
    )


@cabinet_router.callback_query(F.data == 'orders')
async def orders(call: CallbackQuery):
    await call.message.edit_text(
        '<b>Выберите вариант выдачи списка заказов:</b>',
        reply_markup=set_orders_list_keyboard()
    )


@cabinet_router.callback_query(
        F.data.in_(['last_order', 'last_five_orders', 'last_ten_orders']))
async def orders_list(call: CallbackQuery):
    data = call.data
    if data == 'last_order':
        NUMBER_OF_ORDERS = 1
    elif data == 'last_five_orders':
        NUMBER_OF_ORDERS = 5
    else:
        NUMBER_OF_ORDERS = 10
    orders_list = await get_request(ORDERS)
    orders = orders_list['orders']
    message = '<b>Список заказов:</b>\n'
    for order in orders[:NUMBER_OF_ORDERS]:
        number = order['uid']
        amount = order['amount']
        created_at = datetime.fromisoformat(order['created_at'])
        updated_at = datetime.fromisoformat(order['updated_at'])
        delivery_type = order['delivery_type']
        if delivery_type == 1:
            delivery_type = 'С доставкой'
        else:
            delivery_type = 'Самовывоз'
        message += (
            f'<b>Заказ №{number}:</b> \n'
            f'<b>💴Заказ на сумму:</b> {amount} руб. \n'
            f'<b>📅Создан:</b> {created_at.strftime("%d.%m.%Y %H:%M")} \n'
            f'<b>🗓Обновлен:</b> {updated_at.strftime("%d.%m.%Y %H:%M")} \n'
            f'<b>🚚Тип доставки:</b> {delivery_type} \n\n')
    await call.message.edit_text(
        message,
        reply_markup=back_to_cabinet_keyboard()
    )


@cabinet_router.callback_query(F.data == "addresses")
async def addresses_list(call: CallbackQuery):
    response = await get_outlets_info()
    message = "<b>Список адресов доставки:</b>\n\n"
    outlets = [
        delivery for delivery in response if delivery.get('type') == 'co'
    ]
    for outlet in outlets:
        name = outlet['name']
        add_info = outlet['add_info']
        schedule = outlet['schedule']
        message += (
            f"<b>🧾 {name}</b>\n"
            f"<b>💬 Комментарий с уточением к адресу:</b> {add_info}\n"
            f"<b>🕓 Расписание работы:</b> {schedule}\n\n"
        )
    await call.message.edit_text(
        message,
        reply_markup=back_to_cabinet_keyboard()
    )


@cabinet_router.callback_query(F.data == 'set_markup')
async def get_markup(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "<b>Установите наценку на товары, введите новую наценку ниже:</b>",
        reply_markup=back_to_cabinet_keyboard()
    )
    await state.set_state(Markup.wait_for_markup)


@cabinet_router.message(Markup.wait_for_markup)
async def set_markup(message: Message, state: FSMContext):
    markup = message.text
    try:
        markup = float(markup)
        await state.update_data(markup=markup)
        await set_markup_request(markup)
        await message.answer(
            f"<b>Наценка на товары установлена на {markup}%</b>",
            reply_markup=back_to_cabinet_keyboard()
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "<b>Наценка должна быть числом (1.0, 7.5 и т.д.</b>")


@cabinet_router.callback_query(F.data == 'back_to_main')
async def handle_back_to_main_from_cabinet():
    """Возвращает пользователя в главное меню."""
    await send_main_menu()
