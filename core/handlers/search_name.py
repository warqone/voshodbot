import logging
from typing import List, Dict, Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.constants import MIN_SEARCH_QUERY_LENGTH, ITEMS_PER_PAGE
from handlers.start import get_main_menu
from keyboards.start_kb import back_to_main_menu_button
from utils.requests import request_search_name


search_name_router = Router()
logger = logging.getLogger(__name__)


class SearchForm(StatesGroup):
    get_name = State()


class ProductListManager:
    @staticmethod
    async def send_search_prompt(message: Message) -> None:
        """Отправка сообщения с просьбой ввести название запчасти."""
        await message.answer(
            "<b>Для поиска по наименованию введите название запчасти.</b>\n"
            "<i>Пример: \n- масляный фильтр VW Polo\n- воздушный фильтр "
            "vesta</i>",
            reply_markup=back_to_main_menu_button()
        )

    @staticmethod
    def validate_search_query(query: str) -> bool:
        """Проверка длины запроса."""
        return len(query) >= MIN_SEARCH_QUERY_LENGTH

    @staticmethod
    async def process_search_results(
        message: Message,
        search_query: str,
        state: FSMContext,
        bot: Bot
    ) -> None:
        """Поиск результатов и их обработка."""
        try:
            data = await request_search_name(search_query)
            if not data or not data.get('response', {}).get('items'):
                await message.reply(
                    "<b>Товары не найдены. Попробуйте другое название.</b>",
                    reply_markup=back_to_main_menu_button()
                )
                return

            products = data['response']['items']
            await ProductListManager.display_product_page(
                message=message,
                products=products,
                page_number=0,
                state=state,
                bot=bot
            )

        except Exception as e:
            logger.error(f"Ошибка при поиске товаров: {e}", exc_info=True)
            await state.clear()
            await message.answer(
                "<b>Произошла ошибка при поиске. Попробуйте позже.</b>",
                reply_markup=back_to_main_menu_button()
            )

    @staticmethod
    async def display_product_page(
        message: Message,
        products: List[Dict[str, Any]],
        page_number: int,
        state: FSMContext,
        bot: Bot
    ) -> None:
        """Display a page of products with pagination"""
        await state.update_data(products=products, current_page=page_number)

        start_idx = page_number * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        page_products = products[start_idx:end_idx]

        message_text = ProductListManager._build_message_text(
            page_products, page_number)
        keyboard = ProductListManager._build_keyboard(
            page_products, page_number, len(products))

        try:
            await message.edit_text(message_text, reply_markup=keyboard)
        except Exception:
            await message.answer(message_text, reply_markup=keyboard)

    @staticmethod
    def _build_message_text(
            products: List[Dict[str, Any]], page_number: int) -> str:
        """Создаёт текст сообщения с товарами."""
        message_lines = [
            f"<b>Найденные товары:</b>\nСтраница {page_number + 1}\n"
        ]

        for product in products:
            message_lines.extend([
                f"<b>{product['name']}</b>",
                f"<b>Производитель:</b> {product['oem_brand']}",
                f"<b>Артикул:</b> {product['oem_num']}",
                f"<b>Цена:</b> {product['price']} руб.",
                f"<b>Количество на складах:</b> {product['count']}"
                f" {product['unit']}\n"
            ])

        return "\n".join(message_lines)

    @staticmethod
    def _build_keyboard(
        products: List[Dict[str, Any]],
        current_page: int,
        total_products: int
    ) -> InlineKeyboardBuilder:
        """Создаёт клавиатуру с товарами и пагинацией."""
        builder = InlineKeyboardBuilder()

        for product in products:
            builder.button(
                text=f"{product['oem_num']} ({product['price']} руб.)",
                callback_data=f"detail_{product['mog']}"
            )

        navigation_buttons = []
        if current_page > 0:
            navigation_buttons.append(("⬅️ Предыдущая страница", "prev_page"))

        if (current_page + 1) * ITEMS_PER_PAGE < total_products:
            navigation_buttons.append(("Следующая страница ➡️", "next_page"))

        for text, callback_data in navigation_buttons:
            builder.button(text=text, callback_data=callback_data)

        builder.adjust(1)
        return builder.as_markup()


@search_name_router.callback_query(F.data == "search_name")
async def handle_search_name(call: CallbackQuery, state: FSMContext) -> None:
    """Отправляет сообщение с запросом названия запчасти"""
    await call.message.delete()
    await ProductListManager.send_search_prompt(call.message)
    await state.set_state(SearchForm.get_name)


@search_name_router.message(StateFilter(SearchForm.get_name))
async def handle_search_query(
        message: Message, state: FSMContext, bot: Bot) -> None:
    """Возвращает результаты поиска запчастей по наименованию"""
    if not ProductListManager.validate_search_query(message.text):
        await message.answer("<b>Слишком короткое название запчасти.</b>")
        return

    await message.answer(
        f"<b>Поиск запчастей по наименованию: {message.text}...</b>")
    await ProductListManager.process_search_results(
        message, message.text, state, bot)


@search_name_router.callback_query(F.data.in_(["prev_page", "next_page"]))
async def handle_pagination(
        call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Переключает страницу результатов поиска"""
    data = await state.get_data()
    products = data.get("products", [])
    current_page = data.get("current_page", 0)

    if call.data == "prev_page" and current_page > 0:
        current_page -= 1
    elif call.data == "next_page" and (
            current_page + 1) * ITEMS_PER_PAGE < len(products):
        current_page += 1

    await call.answer()
    await ProductListManager.display_product_page(
        message=call.message,
        products=products,
        page_number=current_page,
        state=state,
        bot=bot
    )


@search_name_router.callback_query(F.data == 'back_to_main')
async def handle_back_to_main_from_search(
        call: CallbackQuery, bot: Bot, state: FSMContext):
    """Возвращает пользователя в главное меню."""
    await state.clear()
    await get_main_menu(call.from_user.id, bot)
