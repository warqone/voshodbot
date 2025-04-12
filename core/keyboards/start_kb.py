from aiogram.utils.keyboard import InlineKeyboardBuilder


def token_link_button():
    """Кнопка для получения ключа API"""
    kb = InlineKeyboardBuilder()
    kb.button(text='🔑 Получить ключ API', url='https://v-avto.ru/user/keys')
    return kb.as_markup()


def change_token_button():
    """Кнопка для изменения ключа API"""
    kb = InlineKeyboardBuilder()
    kb.button(text='🔑 Изменить ключ API', callback_data='change_token')
    kb.button(text='✅ Продолжить с текущим ключом',
              callback_data='approve_token')
    kb.adjust(1)
    return kb.as_markup()


def main_menu_buttons():
    """Кнопки главного меню"""
    kb = InlineKeyboardBuilder()
    kb.button(text='🔠 Поиск товара по наименованию',
              callback_data='search_name')
    kb.button(text='#️⃣ Поиск товара по артикулу',
              callback_data='search_cross')
    kb.button(text='⚙️ Личный кабинет', callback_data='account')
    kb.button(text='📓 Справочная', callback_data='info')
    kb.button(text='🧺 Корзина', callback_data='basket')
    kb.adjust(1, 1, 2, 1)
    return kb.as_markup()


def back_to_main_menu_button():
    """Кнопка для возврата в главное меню"""
    kb = InlineKeyboardBuilder()
    kb.button(text='◀️ Вернуться в главное меню', callback_data='back_to_main')
    return kb.as_markup()
