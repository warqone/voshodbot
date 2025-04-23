import logging
from typing import Dict, List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from handlers.constants import BASKET_INFO, BASKET, ITEMS_PER_PAGE
from keyboards.start_kb import back_to_main_menu_button
from keyboards.basket_kb import (
    basket_main_keyboard, basket_edit_keyboard, back_to_basket_button,
    choose_outlets_keyboard, confirm_basket)
from utils.requests import (
    get_request, request_basket_delete, request_add_to_basket,
    get_outlets_info, create_order)

logger = logging.getLogger(__name__)
basket_router = Router()


class BasketEdit(StatesGroup):
    edit = State()


@basket_router.callback_query(F.data.startswith('add_to_basket_'))
async def add_to_basket(call: CallbackQuery,
                        user_api_token: str) -> None:
    """Добавить товар в корзину"""
    try:
        await request_add_to_basket(call.data.split('_')[3], user_api_token)
        await call.answer(
            text='Товар добавлен в корзину. Количество можно изменить в '
            'корзине', show_alert=True
        )
    except Exception as e:
        logger.error(e)


class BasketManager:
    @staticmethod
    async def show_basket(call: CallbackQuery, user_api_token: str):
        """Показать первую страницу корзины"""
        await BasketManager.show_basket_page(call, user_api_token, page=0)

    @staticmethod
    async def show_basket_page(call: CallbackQuery,
                               user_api_token: str,
                               page: int = 0):
        """Показать страницу корзины с пагинацией"""
        try:
            data = await get_request(BASKET, user_api_token)
            items = data.get('items', [])

            if not items:
                await call.answer(
                    text='🗑 Не найдено товаров в корзине.',
                    show_alert=True
                )
                return

            basket_info = await get_request(BASKET_INFO, user_api_token)
            total_price = basket_info['basket']['total_price']
            count = basket_info['basket']['count']

            total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            page_items = items[page * ITEMS_PER_PAGE: (page+1)*ITEMS_PER_PAGE]

            message = await BasketManager.format_basket_message(page_items)
            message += (
                f'\n<b>Страница {page+1} из {total_pages}</b>\n'
                f'<b>Всего товаров:</b> {count}\n'
                f'<b>Общая стоимость:</b> {total_price} руб.')

            kb = InlineKeyboardBuilder()

            main_buttons = basket_main_keyboard().inline_keyboard
            for row in main_buttons:
                kb.row(*row)

            pagination_buttons = []
            if page > 0:
                pagination_buttons.append(
                    InlineKeyboardButton(
                        text="⬅️ Предыдущая страница",
                        callback_data=f"basket_page_{page-1}"
                    )
                )
            if (page+1)*ITEMS_PER_PAGE < len(items):
                pagination_buttons.append(
                    InlineKeyboardButton(
                        text="Следующая страница ➡️",
                        callback_data=f"basket_page_{page+1}"
                    )
                )

            if pagination_buttons:
                kb.row(*pagination_buttons)

            await call.message.edit_text(
                message,
                reply_markup=kb.as_markup()
            )

        except Exception as e:
            logger.error(f'Ошибка при загрузке корзины: {e}')
            await call.answer(
                text='⚠️ Ошибка при загрузке корзины',
                show_alert=True
            )

    @staticmethod
    async def format_basket_message(items: List[Dict]) -> str:
        """Форматирование сообщения с содержимым корзины"""
        message = "<b>🛒 Ваша корзина:</b>\n\n"

        for item in items:
            name = item['name']
            count = item['count']
            unit = item['unit']
            oem_brand = item['oem_brand']
            price = item['price']
            available = (
                "✅ В наличии" if item['available'] else "❌ Нет в наличии")

            message += (
                f"📦 <b>{name}</b>\n"
                f"🏢 Производитель: {oem_brand}\n"
                f"📊 Количество: {count} {unit}\n"
                f"🏷️ Цена: {price} руб.\n"
                f"{available}\n\n"
            )
        return message

    @staticmethod
    async def edit_basket(call: CallbackQuery,
                          user_api_token: str,
                          state: FSMContext):
        """Редактирование корзины"""
        try:
            data = await get_request(BASKET, user_api_token)
            items = data.get('items')
            kb = InlineKeyboardBuilder()
            await state.update_data(basket=items)
            for item in items:
                item_name = item.get('name')
                item_mog = item.get('mog')
                kb.button(
                    text=item_name, callback_data=f'basket_edit_{item_mog}')
            kb.button(text='◀️ Вернуться в корзину', callback_data='basket')
            kb.adjust(1)
            await call.message.edit_text(
                "Выберите товар для редактирования:",
                reply_markup=kb.as_markup()
            )
        except Exception as e:
            logger.error(f"Ошибка редактирования корзины: {e}")
            await call.message.answer(
                "Произошла ошибка при редактировании корзины",
                reply_markup=back_to_main_menu_button()
            )

    @staticmethod
    async def clear_basket(call: CallbackQuery, user_api_token: str):
        """Очистка корзины"""
        try:
            await request_basket_delete(user_api_token)
            await call.message.edit_text(
                "🗑 Корзина очищена.",
                reply_markup=back_to_main_menu_button()
            )
        except Exception as e:
            logger.error(f"Ошибка очистки корзины: {e}")
            await call.message.answer(
                "Произошла ошибка при очистке корзины",
                reply_markup=back_to_main_menu_button()
            )


@basket_router.callback_query(F.data == 'basket')
async def handle_basket(call: CallbackQuery, user_api_token: str):
    """Обработчик корзины"""
    await BasketManager.show_basket(call, user_api_token)


@basket_router.callback_query(F.data == 'clear_basket')
async def handle_clear(call: CallbackQuery, user_api_token: str):
    """Обработчик очистки корзины"""
    await BasketManager.clear_basket(call, user_api_token)


@basket_router.callback_query(F.data == 'edit_basket')
async def handle_edit(call: CallbackQuery,
                      user_api_token: str,
                      state: FSMContext):
    """Обработчик редактирования корзины"""
    await BasketManager.edit_basket(call, user_api_token, state)


@basket_router.callback_query(F.data.startswith('basket_page_'))
async def handle_basket_pagination(call: CallbackQuery, user_api_token: str):
    """Обработчик пагинации корзины"""
    page = int(call.data.split('_')[-1])
    await BasketManager.show_basket_page(call, user_api_token, page)


@basket_router.callback_query(F.data.startswith('basket_edit_'))
async def handle_basket_edit(call: CallbackQuery,
                             user_api_token: str,
                             state: FSMContext):
    """Обработчик редактирования товара в корзине"""
    mog = call.data.split('_')[-1]
    data = await state.get_data()
    basket = data.get('basket')
    choosed_item = next(
        (item for item in basket if item.get('mog') == mog), None)
    await state.update_data(choosed_item=choosed_item)
    await call.message.edit_text(
        f'Редактирование товара: <b>{choosed_item.get("name")}</b>',
        reply_markup=basket_edit_keyboard()
    )


@basket_router.callback_query(F.data == 'edit_quantity')
async def handle_edit_quantity(call: CallbackQuery,
                               user_api_token: str,
                               state: FSMContext):
    """Обработчик редактирования количества товара в корзине"""
    data = await state.get_data()
    choosed_item = data.get('choosed_item')
    await call.message.edit_text(
        f'Редактирование количества товара: <b>{choosed_item.get("name")}</b>'
        '\nВведите новое количество ниже:',
        reply_markup=back_to_basket_button()
    )
    await state.set_state(BasketEdit.edit)


@basket_router.message(StateFilter(BasketEdit.edit))
async def handle_edit_quantity_message(message: Message,
                                       user_api_token: str,
                                       state: FSMContext):
    """Обработчик сообщения с новым количеством товара в корзине"""
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля.")
    except ValueError:
        await message.answer(
            '❗ <b>Ошибка!</b>\n'
            'Введите целое число больше нуля\n\n'
            'Пример: <code>5</code>'
        )
        return

    data = await state.get_data()
    choosed_item = data.get('choosed_item')
    await state.clear()

    try:
        await request_add_to_basket(
            choosed_item.get('mog'), user_api_token, quantity)
        await message.answer(
            f'✅ Количество товара <b>{choosed_item.get("name")}</b> '
            f'изменено на {quantity}',
            reply_markup=back_to_basket_button()
        )
    except Exception:
        await message.answer(
            '❗ <b>Ошибка при обновлении количества</b>'
        )


@basket_router.callback_query(F.data == 'delete_item')
async def handle_back_to_basket(call: CallbackQuery,
                                user_api_token: str,
                                state: FSMContext):
    """Обработчик удаления товара из корзины."""
    data = await state.get_data()
    choosed_item = data.get('choosed_item')
    await state.clear()

    try:
        await request_add_to_basket(
            choosed_item.get('mog'), user_api_token, quantity=0)
        await call.answer(
            '❌ Товар удален из корзины',
            show_alert=True
        )
    except Exception:
        await call.answer(
            'Произошла ошибка при удалении товара из корзины',
            show_alert=True
        )


@basket_router.callback_query(F.data == 'checkout_basket')
async def handle_checkout_basket(call: CallbackQuery, state: FSMContext):
    """Обработчик оформления заказа."""
    await call.message.edit_text(
        '<b>Выберите тип доставки:</b>',
        reply_markup=choose_outlets_keyboard()
    )


@basket_router.callback_query(F.data.in_({'basket_va', 'basket_co'}))
async def handle_choose_basket(call: CallbackQuery,
                               user_api_token: str,
                               state: FSMContext):
    """Обработчик выбора типа доставки."""
    delivery_type = call.data.split('_')[-1]
    if call.data == 'basket_va':
        message = '<b>Выберите адрес для самовывоза:</b>'
    else:
        message = '<b>Выберите адрес для доставки:</b>'
    await state.update_data(delivery_type=delivery_type)
    response = await get_outlets_info(user_api_token)
    outlets = [
        out for out in response if out.get('type') == delivery_type
    ]
    if not outlets:
        return await call.answer(
            'Список точек пуст.',
            show_alert=True
        )
    kb = InlineKeyboardBuilder()
    addresses = {}
    for outlet in outlets:
        address = outlet.get('name')
        id = outlet.get('id')
        addresses[id] = address
        kb.button(text=outlet.get('name'),
                  callback_data=f'basket_outlet_{outlet.get("id")}')
    kb.button(text='🛒 Вернуться в корзину', callback_data='basket')
    kb.adjust(1)
    await state.update_data(addresses=addresses)
    await call.message.edit_text(
        message,
        reply_markup=kb.as_markup())


@basket_router.callback_query(F.data.startswith('basket_outlet_'))
async def handle_choose_outlet(call: CallbackQuery,
                               user_api_token: str,
                               state: FSMContext):
    """Обработчик выбора точки доставки."""
    outlet_id = call.data.split('_')[-1]
    await state.update_data(outlet_id=outlet_id)
    data = await state.get_data()
    addresses = data.get('addresses')
    address = addresses[outlet_id]
    delivery_type = data.get('delivery_type')
    if delivery_type == 'va':
        message = f'<b>Вы выбрали точку самовывоза:</b>\n{address}\n\n'
    else:
        message = f'<b>Вы выбрали точку доставки:</b>\n{address}\n\n'
    message += '<b>Для оформления заказа нажмите кнопку "Оформить заказ".</b>'
    await call.message.edit_text(
        message, reply_markup=confirm_basket()
    )


@basket_router.callback_query(F.data == 'confirm_basket')
async def handle_confirm_basket(call: CallbackQuery,
                                user_api_token: str,
                                state: FSMContext):
    """Обработчик подтверждения заказа."""
    data = await state.get_data()
    outlet_id = data.get('outlet_id')
    response = await create_order(user_api_token, outlet_id)
    response = response.get('response')
    order = response.get('order')
    if not order:
        return await call.answer(
            'Произошла ошибка при оформлении заказа.',
            show_alert=True
        )
    order_id = order.get('uid', '')
    amount = order.get('amount', 0)
    addresses = data.get('addresses')
    delivery_address = addresses[outlet_id]
    await call.answer(
        f'Заказ №{order_id} оформлен.',
        show_alert=True
    )
    await call.message.edit_text(
        f'<b>Заказ оформлен.\n#️⃣ Номер заказа:</b> {order_id}\n'
        f'<b>🛒 Сумма заказа:</b> {amount}\n'
        f'<b>🚖 Адрес доставки:</b> {delivery_address}',
        reply_markup=back_to_main_menu_button()
    )
    await state.clear()
