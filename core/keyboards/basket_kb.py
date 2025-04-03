from aiogram.utils.keyboard import InlineKeyboardBuilder


def basket_main_keyboard() -> InlineKeyboardBuilder:
    """Создание клавиатуры для корзины"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🧹 Очистить", callback_data="clear_basket")
    builder.button(text="🚖 Оформить", callback_data="checkout_basket")
    builder.adjust(1)
    return builder.as_markup()
