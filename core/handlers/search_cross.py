from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from handlers.constants import ITEMS_PER_PAGE, MIN_SEARCH_QUERY_LENGTH
from keyboards.start_kb import back_to_main_menu_button
from utils.requests import request_search_cross
from utils.utils import formatting_items


class SearchCross(StatesGroup):
    search_cross = State()
    search_cross_brand = State()


search_cross_router = Router()


@search_cross_router.callback_query(F.data == "search_cross")
async def search_cross(call: CallbackQuery, state: FSMContext):
    """Поиск товара по артикулу."""
    await call.message.edit_text(
        '<b>Для поиска товара по артикулу введите артикул.</b>\n'
        '<i>Пример:\n-C25011\n-K015670XS</i>',
        reply_markup=back_to_main_menu_button()
    )
    await state.set_state(SearchCross.search_cross)


@search_cross_router.message(StateFilter(SearchCross.search_cross))
async def search_cross_brand(message: Message,
                             state: FSMContext,
                             user_api_token: str):
    """Результат поиска товара по артикулу (уточнение бренда)."""
    if len(message.text) < MIN_SEARCH_QUERY_LENGTH:
        await message.answer(
            '<b>Слишком короткий артикул.</b>'
        )
        return
    await message.answer(
        f'<b>Производим поиск товара по артикулу: {message.text}</b>'
    )
    try:
        response = await request_search_cross(message.text, user_api_token)
        brands = response.get('brands')
        if brands:
            kb = InlineKeyboardBuilder()
            for brand in brands:
                name_of_brand = brand.get('brand')
                article = brand.get('oem')
                if article:
                    callback_data = f'cross_detail_{name_of_brand}_{article}'
                else:
                    callback_data = f'cross_detail_{name_of_brand}_{article}'
                kb.button(
                    text=name_of_brand,
                    callback_data=callback_data
                )
            kb.adjust(2)
            await message.answer(
                '<b>Выберите бренд производителя:</b>',
                reply_markup=kb.as_markup()
            )
        else:
            await message.answer(
                '<b>Товар не найден.</b>\nПопробуйте ввести другой артикул.',
                reply_markup=back_to_main_menu_button()
            )
    except Exception:
        await message.answer(
            '<b>Произошла ошибка при поиске товара по артикулу.</b>'
        )


@search_cross_router.callback_query(F.data.startswith('cross_detail_'))
async def cross_detail(call: CallbackQuery,
                       state: FSMContext,
                       user_api_token: str):
    """Результат поиска товара по артикулу (после уточнения бренда)."""
    await call.message.delete()
    brand = call.data.split('_')[2]
    article = call.data.split('_')[3]
    response = await request_search_cross(
        article, user_api_token, brand
    )
    target = response.get('target', [])
    items = response.get('items', [])
    image = ''
    kb = InlineKeyboardBuilder()
    if items:
        await state.update_data(analogs=items)
        kb.button(text='💬 Показать аналоги', callback_data='show_analogs')
    if target:
        target = target[0]
        image = target.get('images')[0]
        message = await formatting_items(target)
        if target.get('count') > 0:
            kb.button(
                text='🛒 Добавить в корзину',
                callback_data=f'add_to_basket_{target.get("mog")}')
    else:
        message = '<b>Товар с заданным артикулом и брендом не найден.</b>'
    kb.button(text='◀️ Вернуться в главное меню', callback_data='back_to_main')
    kb.adjust(1)
    if image:
        try:
            await call.message.answer_photo(
                image,
                caption=message,
                reply_markup=kb.as_markup()
            )
        except Exception:
            await call.message.answer(
                f'Фото загрузить не удалось\n\n{message}',
                reply_markup=kb.as_markup()
            )
    else:
        await call.message.answer(
            message,
            reply_markup=kb.as_markup()
        )


@search_cross_router.callback_query(F.data == 'show_analogs')
async def show_analogs(call: CallbackQuery, state: FSMContext):
    """Показать аналоги (первая страница)."""
    await call.message.delete()
    data = await state.get_data()
    analogs = data.get('analogs', [])

    avalaible_analogs = [
        analog for analog in analogs if analog.get('count') > 0]

    if not avalaible_analogs:

        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer(
            '<b>Аналоги не найдены.</b>',
            reply_markup=back_to_main_menu_button()
        )
        return

    sent_message = await call.message.answer(
        '<b>Загружаю аналоги...</b>'
    )

    await show_analogs_page(sent_message, avalaible_analogs, page=0)


async def show_analogs_page(message, analogs, page=0):
    """Показать страницу с аналогами."""
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = analogs[start_idx:end_idx]

    kb = InlineKeyboardBuilder()

    message_text = '<b>Аналоги:</b>\n\n'
    for idx, analog in enumerate(page_items, start=start_idx + 1):
        message_text += await formatting_items(analog)
        article = analog.get('oem_num', 'Не указан')
        price = analog.get('price', 'Не указана')
        brand = analog.get('oem_brand', 'Не указан')
        kb.button(
            text=(
                f"{article} "
                f"({price}) руб."
            ), callback_data=f"cross_detail_{brand}_{article}"
        )
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Предыдущая страница",
            callback_data=f"analogs_page_{page - 1}"
        ))
    if end_idx < len(analogs):
        pagination_buttons.append(InlineKeyboardButton(
            text="Следующая страница ➡️",
            callback_data=f"analogs_page_{page + 1}"
        ))

    if pagination_buttons:
        kb.row(*pagination_buttons)
    kb.button(text='Вернуться в главное меню', callback_data='back_to_main')
    kb.adjust(1)

    await message.edit_text(
        message_text,
        reply_markup=kb.as_markup()
    )


@search_cross_router.callback_query(F.data.startswith('analogs_page_'))
async def handle_analogs_pagination(call: CallbackQuery, state: FSMContext):
    """Обработчик переключения страниц с аналогами."""
    await call.answer()
    page = int(call.data.split('_')[-1])

    data = await state.get_data()
    analogs = data.get('analogs', [])
    avalaible_analogs = [
        analog for analog in analogs if analog.get('count') > 0]

    await show_analogs_page(call.message, avalaible_analogs, page)
