from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.cabinet_kb import (
    cabinet_keyboard, back_to_cabinet_keyboard, set_orders_list_keyboard,
    outlets_va_keyboard)
from handlers.constants import MARKUP_URL
from handlers.start import send_main_menu
from utils.requests import (
    get_request, get_outlets_info, set_markup_request, get_orders_info)

cabinet_router = Router()


class Markup(StatesGroup):
    wait_for_markup = State()


@cabinet_router.callback_query(F.data == "account")
async def account_info(call: CallbackQuery,
                       state: FSMContext,
                       user_api_token: str):
    await state.clear()
    data = await get_request(MARKUP_URL, user_api_token)
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
async def orders_list(call: CallbackQuery, user_api_token: str):
    data = call.data
    if data == 'last_order':
        NUMBER_OF_ORDERS = 1
    elif data == 'last_five_orders':
        NUMBER_OF_ORDERS = 5
    else:
        NUMBER_OF_ORDERS = 10
    orders_list = await get_orders_info(user_api_token)
    orders = orders_list.get('orders')
    if not orders:
        return await call.answer(
            'Список заказов пуст.',
            show_alert=True
        )
    message = '<b>Список заказов:</b>\n'
    for order in orders[:NUMBER_OF_ORDERS]:
        number = order.get('uid', 'Номер не найден')
        amount = order.get('amount',  'Сумма не найдена')
        delivery_period = order.get('delivery_period')
        start_date = datetime.fromisoformat(delivery_period.get('start_time'))
        end_date = datetime.fromisoformat(delivery_period.get('end_time'))
        created_at = datetime.fromisoformat(order.get('created_at'))
        start_date_str = start_date.strftime("%d.%m.%Y %H:%M")
        end_date_str = end_date.strftime("%d.%m.%Y %H:%M")
        message += (
            f'<b>Заказ №{number}:</b> \n'
            f'<b>💴Заказ на сумму:</b> {amount} руб. \n'
            f'<b>📅Создан:</b> {created_at.strftime("%d.%m.%Y %H:%M")} \n'
            f'<b>🕓 Время доставки/получения:</b> {start_date_str} - '
            f'{end_date_str}\n\n')
    await call.message.edit_text(
        message,
        reply_markup=back_to_cabinet_keyboard()
    )


@cabinet_router.callback_query(F.data == "outlets")
async def outlets_list(call: CallbackQuery, user_api_token: str):
    response = await get_outlets_info(user_api_token)
    message = "<b>Список адресов доставки:</b>\n\n"
    outlets = [
        delivery for delivery in response if delivery.get('type') == 'co'
    ]
    if not outlets:
        return await call.answer(
            'Список адресов доставки пуст.',
            show_alert=True
        )
    for outlet in outlets:
        add_info = outlet.get('add_info', 'Название не найдено')
        name = outlet.get('name', 'Адрес не найден')
        schedule = outlet.get('schedule', 'Расписание работы не найдено')
        message += (
            f"<b>🧾 {name}</b>\n"
            f"<b>💬 Комментарий с уточением к адресу:</b> {add_info}\n"
            f"<b>🕓 Расписание работы:</b> {schedule}\n\n"
        )
    await call.message.edit_text(
        message,
        reply_markup=outlets_va_keyboard()
    )


@cabinet_router.callback_query(F.data == 'outlets_va')
async def outlets_va(call: CallbackQuery, user_api_token: str):
    response = await get_outlets_info(user_api_token)
    outlets = [
        delivery for delivery in response if delivery.get('type') == 'va'
    ]
    if not outlets:
        return await call.answer(
            'Список точек для самовывоза пуст.',
            show_alert=True
        )
    message = '<b>Список точек для самовывоза:</b>\n\n'
    for outlet in outlets:
        add_info = outlet.get('add_info', 'Название не найдено')
        name = outlet.get('name', 'Адрес не найден')
        schedule = outlet.get('schedule', 'Расписание работы не найдено')
        message += f"🧾<b>{add_info}</b>\n💬{name}\n🕓{schedule}\n\n"
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
async def set_markup(message: Message,
                     state: FSMContext,
                     user_api_token: str):
    markup = message.text
    try:
        markup = float(markup)
        await state.update_data(markup=markup)
        await set_markup_request(markup, user_api_token)
        await message.answer(
            f"<b>Наценка на товары установлена на {markup}%</b>",
            reply_markup=back_to_cabinet_keyboard()
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "<b>Наценка должна быть числом (1.0, 7.5 и т.д.)</b>")


@cabinet_router.callback_query(F.data == 'back_to_main')
async def handle_back_to_main_from_cabinet():
    """Возвращает пользователя в главное меню."""
    await send_main_menu()
