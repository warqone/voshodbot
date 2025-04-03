from aiogram.utils.keyboard import InlineKeyboardBuilder


def cabinet_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='📋 Список заказов', callback_data='orders')
    kb.button(text='📈 Изменить наценку', callback_data='set_markup')
    kb.button(text='🚚 Список адресов доставки', callback_data='addresses')
    kb.button(text='◀️ В главное меню', callback_data='back_to_main')
    kb.adjust(1)
    return kb.as_markup()


def set_orders_list_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='Последний заказ', callback_data='last_order')
    kb.button(text='Последние 5 заказов', callback_data='last_five_orders')
    kb.button(text='Последние 10 заказов', callback_data='last_ten_orders')
    kb.adjust(1)
    return kb.as_markup()


def back_to_cabinet_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='◀️ Вернуться в кабинет', callback_data='account')
    return kb.as_markup()
