from aiogram.utils.keyboard import InlineKeyboardBuilder


def basket_main_keyboard() -> InlineKeyboardBuilder:
    """Создание клавиатуры для корзины"""
    kb = InlineKeyboardBuilder()
    kb.button(text='Редактировать', callback_data='edit_basket')
    kb.button(text='🧹 Очистить', callback_data='clear_basket')
    kb.button(text='🚖 Оформить', callback_data='checkout_basket')
    kb.button(text='◀️ Вернуться в меню', callback_data='back_to_main')
    kb.adjust(1)
    return kb.as_markup()
