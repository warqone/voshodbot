from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.start_kb import back_to_main_menu_button

search_name_router = Router()


class SearchForm(StatesGroup):
    get_name = State()


@search_name_router.callback_query(F.data == 'search_name')
async def search_name(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        '<b>Для поиска по наименованию введите название запчасти.</b>\n'
        '<i>Пример: \n- масляный фильтр VW Polo\n- воздушный фильтр vesta</i>',
        reply_markup=back_to_main_menu_button()
    )
    await state.set_state(SearchForm.get_name)


@search_name_router.message(StateFilter(SearchForm.get_name))
async def get_search_name(message: Message):
    name = message.text
    try:
        
