from aiogram.utils.keyboard import InlineKeyboardBuilder


def info_kb():
    """Клавиатура справочной."""
    kb = InlineKeyboardBuilder()
    kb.button(text='🎁 Акции и спецпредложения', url='https://v-avto.ru/sales')
    kb.button(text='🧩 Онлайн-подбор', url='https://t.me/voshodbot')
    kb.button(text='◀️ В главное меню', callback_data='back_to_main')
    kb.adjust(1)
    return kb.as_markup()
