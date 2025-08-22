from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_inline_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Записаться на тренировку', callback_data='choose_pool_type_state')
    keyboard_builder.button(text='Удалить запись с тренировки', callback_data='booking_delete')
    keyboard_builder.button(text='Посмотреть последние тренировки', callback_data='training_info')
    keyboard_builder.button(text='Посмотреть баланс', callback_data='balance_view')
    keyboard_builder.button(text='Пополнить баланс', callback_data='balance_update')
    keyboard_builder.button(text='Привязать нового ребенка', callback_data='add_child_remote')
    keyboard_builder.button(text='Отвязать ребенка', callback_data='child_delete')
    keyboard_builder.button(text='Подробнее о тренерах', callback_data='trainer_info')
    keyboard_builder.button(text='Переключиться на другого ребенка', callback_data='child_switch')
    keyboard_builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)
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
    for idx, training in enumerate(trainings_list):
        # Use compact callback data to keep under Telegram's 64-byte limit
        keyboard_builder.button(text=training, callback_data=f"tr_{idx}")
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

def child_names_choosing_keyboard_with_back_button(child_list):
    keyboard_builder = InlineKeyboardBuilder()
    for child in child_list:
        keyboard_builder.button(text=child, callback_data=child)
    keyboard_builder.button(text='Назад', callback_data='back')
    keyboard_builder.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()


def pool_type_keyboard_with_back_button():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Большой бассейн 🐬', callback_data='pool_big')
    keyboard_builder.button(text='Малый бассейн 🐠', callback_data='pool_small')
    keyboard_builder.button(text='Любой бассейн', callback_data='pool_any')
    keyboard_builder.button(text='Назад', callback_data='back')
    keyboard_builder.adjust(1, 1, 1, 1)
    return keyboard_builder.as_markup()


def trainer_list_keyboard_with_back_button(trainers_list):
    keyboard_builder = InlineKeyboardBuilder()
    for trainer in trainers_list:
        keyboard_builder.button(text=trainer, callback_data=f"trainer_{trainer}")
    keyboard_builder.button(text="Любой тренер", callback_data="trainer_any")
    keyboard_builder.button(text="Назад", callback_data="back")
    keyboard_builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()


def trainer_list_for_info_keyboard_with_back_button(trainers_list):
    keyboard_builder = InlineKeyboardBuilder()
    for trainer in trainers_list:
        keyboard_builder.button(text=trainer, callback_data=f"{trainer}")
    keyboard_builder.button(text="Назад", callback_data="back")
    keyboard_builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()
