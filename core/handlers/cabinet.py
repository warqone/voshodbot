from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from keyboards.cabinet_kb import (
    cabinet_keyboard, back_to_cabinet_keyboard, set_orders_list_keyboard)
from handlers.constants import ORDERS, MARKUP_URL, ORDERS_DELIVERIES
from handlers.start import send_main_menu
from utils.requests import get_request

cabinet_router = Router()


@cabinet_router.callback_query(F.data == "account")
async def account_info(call: CallbackQuery):
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
    response = await get_request(ORDERS_DELIVERIES)
    deliveries = response['deliveries']
    message = "<b>Список адресов доставки:</b>\n\n"
    for delivery in deliveries:
        name = delivery['name']
        updated_at = datetime.fromisoformat(delivery['updated_at'])
        message += (
            f"<b>{name}</b>\n"
            f"<b>Создан:</b> {updated_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
    await call.message.edit_text(
        message,
        reply_markup=back_to_cabinet_keyboard()
    )


@cabinet_router.callback_query(F.data == 'set_markup')
async def get_markup(call: CallbackQuery):
    await call.message.edit_text(
        "<b>Установите наценку на товары:</b>",
        reply_markup=cabinet_keyboard()
    )


@cabinet_router.callback_query(F.data == 'back_to_main')
async def handle_back_to_main_from_cabinet(call: CallbackQuery):
    """Возвращает пользователя в главное меню."""
    await send_main_menu()
