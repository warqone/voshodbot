from aiogram.utils.keyboard import InlineKeyboardBuilder


def basket_main_keyboard() -> InlineKeyboardBuilder:
    """Создание клавиатуры для корзины"""
    kb = InlineKeyboardBuilder()
    kb.button(text='📝 Редактировать', callback_data='edit_basket')
    kb.button(text='🧹 Очистить', callback_data='clear_basket')
    kb.button(text='🚖 Оформить', callback_data='checkout_basket')
    kb.button(text='Вернуться в меню', callback_data='back_to_main')
    kb.adjust(1, 2, 1)
    return kb.as_markup()


def basket_edit_keyboard() -> InlineKeyboardBuilder:
    """Создание клавиатуры для редактирования корзины"""
    kb = InlineKeyboardBuilder()
    kb.button(text='📦 Изменить количество', callback_data='edit_quantity')
    kb.button(text='❌ Удалить товар', callback_data='delete_item')
    kb.button(text='🛒 Вернуться в корзину', callback_data='basket')
    kb.adjust(1)
    return kb.as_markup()


def back_to_basket_button() -> InlineKeyboardBuilder:
    """Создание клавиатуры для возврата в корзину"""
    kb = InlineKeyboardBuilder()
    kb.button(text='🛒 Вернуться в корзину', callback_data='basket')
    return kb.as_markup()


def choose_outlets_keyboard() -> InlineKeyboardBuilder:
    """Создание клавиатуры для выбора точки самовывоза"""
    kb = InlineKeyboardBuilder()
    kb.button(text='🚚 САМОВЫВОЗ', callback_data='basket_va')
    kb.button(text='🚖 ДОСТАВКА', callback_data='basket_co')
    kb.button(text='🛒 Вернуться в корзину', callback_data='basket')
    kb.adjust(2, 1)
    return kb.as_markup()


def confirm_basket() -> InlineKeyboardBuilder:
    """Создание клавиатуры для подтверждения корзины"""
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Оформить заказ', callback_data='confirm_basket')
    return kb.as_markup()
