from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.constants import MIN_SEARCH_QUERY_LENGTH
from keyboards.start_kb import back_to_main_menu_button
from utils.requests import request_search_cross


class SearchCross(StatesGroup):
    search_cross = State()
    search_cross_brand = State()


search_cross_router = Router()


@search_cross_router.callback_query(F.data == "search_cross")
async def search_cross(call: CallbackQuery, state: FSMContext):
    """Поиск товара по артикулу."""
    await call.message.edit_text(
        '<b>Для поиска товара по артикулу введите артикул.</b>\n'
        '<i>Пример:\nGB123\nGB-102M</i>',
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
            await state.update_data(article=message.text)
            kb = InlineKeyboardBuilder()
            for brand in brands:
                name_of_brand = brand.get('brand')
                kb.button(
                    text=name_of_brand,
                    callback_data=f'cross_detail_{name_of_brand}'
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
    data = await state.get_data()
    article = data.get('article')
    brand = call.data.split('_')[2]
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
        message = (
            f"📦 <b>{target.get('name', 'Название не указано')}</b>\n"
            f"🏢 <b>Производитель:</b> {target.get('oem_brand', 'Не указан')}\n"
            f"🔢 <b>Артикул:</b> {target.get('oem_num', 'Не указан')}\n"
            f"🏷️ <b>Цена:</b> {target.get('price', 'Не указана')} руб.\n"
            f"<b>Количество на складах:</b> {target.get('count', 0)} "
            f"{target.get('unit', 'шт')}\n"
            "<b>Количество на складах Челябинска:</b> "
            f"{target.get('count_chel', 0)} {target.get('unit', 'шт')}\n"
            "<b>Количество на складах Екатеринбурга:</b> "
            f"{target.get('count_ekb', 0)} {target.get('unit', 'шт')}\n"
        )
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
    """Показать аналоги."""
    await call.message.delete()
    data = await state.get_data()
    analogs = data.get('analogs', [])
    if analogs:
        avalaible_analogs = [
            analog for analog in analogs if analog.get('count') > 0
        ]
        kb = InlineKeyboardBuilder()
        message = '<b>Аналоги:</b>\n'
        if avalaible_analogs:
            for analog in avalaible_analogs:
                message += (f'{analog.get("name", "Название не указано")}\n'
                            f'{analog.get("price", "Цена не указана")} руб.\n'
                            f'{analog.get("count", "Количество не указано")} '
                            f'{analog.get("unit", "шт")}'
                )
                kb.button(
                    text=analog.get('name', 'Название не указано'),
                    callback_data=f'cross_detail_{analog.get("mog")}'
                )
                kb.adjust(1)
            await call.message.answer(
                '<b>Аналоги:</b>\n',
                reply_markup=kb.as_markup()
            )
    else:
        await call.message.answer(
            '<b>Аналоги не найдены.</b>',
            reply_markup=back_to_main_menu_button()
        )
        return
    # kb = InlineKeyboardBuilder()
    # for analog in analogs:
    #     kb.button(
    #         text=analog.get('name', 'Название не указано'),
    #         callback_data=f'cross_detail_{analog.get("mog")}'
    #     )
