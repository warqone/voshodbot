import logging
from typing import Dict, List

from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.constants import BASKET_INFO, BASKET
from keyboards.start_kb import back_to_main_menu_button
from keyboards.basket_kb import basket_main_keyboard
from utils.requests import get_request, request_basket_delete

logger = logging.getLogger(__name__)
basket_router = Router()


class BasketManager:
    @staticmethod
    async def show_basket(call: CallbackQuery) -> None:
        """Показать содержимое корзины"""
        try:
            data = await get_request(BASKET)
            items = data['items']
            if len(items) == 0:
                await call.answer(
                    text='🗑 Не найдено товаров в корзине.',
                    show_alert=True
                )
                return
            basket_info = await get_request(BASKET_INFO)
            total_price = basket_info['basket']['total_price']
            count = basket_info['basket']['count']
            message = await BasketManager.format_basket_message(items)
            message += (
                f'\n\n<b>Всего товаров:</b> {count}\n'
                f'<b>Общая стоимость:</b> {total_price} руб.')
            await call.message.edit_text(
                message,
                reply_markup=basket_main_keyboard()
            )

        except Exception as e:
            logger.error(f'Ошибка при запросе корзины: {e}', exc_info=True)
            await call.message.answer(
                'Произошла внутренняя ошибка. Попробуйте позже.',
                reply_markup=back_to_main_menu_button()
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
                f"<b>{name}</b>\n"
                f"Производитель: {oem_brand}\n"
                f"Количество: {count} {unit}\n"
                f"Цена: {price} руб.\n"
                f"Статус: {available}\n\n"
            )
        return message

    @staticmethod
    async def clear_basket(call: CallbackQuery) -> None:
        """Очистка корзины"""
        try:
            await request_basket_delete()
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
async def handle_basket(call: CallbackQuery):
    await BasketManager.show_basket(call)


@basket_router.callback_query(F.data == 'clear_basket')
async def handle_clear(call: CallbackQuery):
    await BasketManager.clear_basket(call)
