from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_inline_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Записаться на тренировку', callback_data='training_register')
    keyboard_builder.button(text='Удалить запись с тренировки', callback_data='booking_delete')
    keyboard_builder.button(text='Посмотреть последние тренировки', callback_data='training_info')
    keyboard_builder.button(text='Посмотреть баланс', callback_data='balance_view')
    keyboard_builder.button(text='Пополнить баланс', callback_data='balance_update')
    keyboard_builder.adjust(1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()


def update_balance_inline_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='1', callback_data='add_balance_trainings_1')
    keyboard_builder.button(text='4', callback_data='add_balance_trainings_4')
    keyboard_builder.button(text='8', callback_data='add_balance_trainings_8')
    keyboard_builder.button(text='12', callback_data='add_balance_trainings_12')
    keyboard_builder.button(text='Назад', callback_data='back')
    keyboard_builder.adjust(1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()


def back_button():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Назад', callback_data='back')
    return keyboard_builder.as_markup()


def training_booking_keyboard(trainings_list):
    keyboard_builder = InlineKeyboardBuilder()
    for training in trainings_list:
        keyboard_builder.button(text=training, callback_data=training)
    keyboard_builder.button(text='Назад', callback_data='back')
    keyboard_builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()


def training_booking_confirm_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Записаться', callback_data='confirm_training')
    keyboard_builder.button(text='Назад', callback_data='back')
    keyboard_builder.adjust(1, 1)
    return keyboard_builder.as_markup()

def booking_accept_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Назад в меню', callback_data='back')
    return keyboard_builder.as_markup()

def booking_cancel_choose_keyboard(trainings_list):
    keyboard_builder = InlineKeyboardBuilder()
    for training in trainings_list:
        keyboard_builder.button(text=training, callback_data=training)
    keyboard_builder.button(text='Назад', callback_data='back')
    keyboard_builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()


def booking_cancel_info_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Удалить запись', callback_data='booking_cancel')
    keyboard_builder.button(text='Назад', callback_data='back')
    keyboard_builder.adjust(1, 1)
    return keyboard_builder.as_markup()


def child_names_choosing_keyboard(child_list):
    keyboard_builder = InlineKeyboardBuilder()
    for child in child_list:
        keyboard_builder.button(text=child, callback_data=child)
    keyboard_builder.adjust(1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()