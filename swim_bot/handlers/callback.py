from datetime import datetime

from aiogram import Bot
from aiogram.fsm import state
from database.db_query_funcs import child_name_id_write, get_child_balance, get_child_name, get_child_trainings, get_trainings_list, child_training_register, child_training_register_delete, balance_update_db, operation_add_to_story, delete_child_remote, get_trainings_list_for_booking
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline import back_button, training_booking_keyboard, training_booking_confirm_keyboard, booking_accept_keyboard, booking_cancel_choose_keyboard, booking_cancel_info_keyboard, update_balance_inline_keyboard, child_names_choosing_keyboard, child_names_choosing_keyboard_with_back_button
from handlers.basic import main_menu_handler, start, cancel
from utils.states import MainStates
from utils.info_validation import valid_training_date_check, valid_training_message_text, valid_training_date_check_booking

async def current_child_save(call: CallbackQuery, bot: Bot, state: FSMContext):
    child_name = call.data
    tg_chat_id = call.message.chat.id
    await child_name_id_write(tg_chat_id, child_name)
    await state.set_state(MainStates.menu_open)
    await main_menu_handler(call.message, state)
    await call.message.delete()

async def back_button_callback(call: CallbackQuery, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MainStates.confirm_booking:
        await training_booking(call, bot, state)
    elif current_state == MainStates.booking_cancel_confirm:
        await booking_cancel_choose(call, bot, state)
    else:
        await state.set_state(MainStates.menu_open)
        await main_menu_handler(call.message, state)
        await call.message.delete()

async def view_stats(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.view_stats)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    trainings_info = await get_child_trainings(child_name)
    text = ''
    for training in trainings_info:
        text += f"Тренировка {training['date']}\n"
        text += f"Время: {training['time']}\n"
        text += f"Тип бассейна: {training['pool_type']}\n"
        text += f"Тренер: {training['trainer_name']}\n\n"
    await call.message.answer(text=f'Информация по последним тренировкам, на которые вы записаны (максимум 10) \n \n{text}', reply_markup=back_button())
    await call.message.delete()

async def view_balance(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.view_balance)
    child_name = await get_child_name(chat_id=call.message.chat.id, table_name='backend_childid')
    result = await get_child_balance(child_name)
    user_balance = result[0]['paid_training_count']
    await call.message.answer(text=f'Остаток оплаченных тренировок на балансе - {user_balance}', reply_markup=back_button())
    await call.message.delete()


async def training_booking(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.choose_training_date)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    trainings_list_of_dict = await get_trainings_list(child_name)
    trainings_list = []
    for training in trainings_list_of_dict:
        text = ''
        text += f"{training['date']} "
        text += f"{training['time']} "
        trainings_list.append(text)
    await call.message.answer(text='Выберите тренировку из списка', reply_markup=training_booking_keyboard(trainings_list))
    await call.message.delete()


async def booking_info_confirm(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.confirm_booking)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    trainings_list_of_dict = await get_trainings_list_for_booking(child_name)
    text = valid_training_date_check_booking(call.data, trainings_list_of_dict)
    await call.message.answer(text=f'Полная информация по тренировке: \n \n'
                                   f'{text}', reply_markup=training_booking_confirm_keyboard())
    await call.message.delete()


async def booking_accept(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.booking_accept)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    date_value, time_value = valid_training_message_text(call.message.text)
    res = await child_training_register(child_name, date_value, time_value)
    balance = await get_child_balance(child_name)
    current_balance = int(balance[0]['paid_training_count'])
    if current_balance == 0:
        balance_alert = f'Остаток на балансе: ⚠️ 0 ⚠️'
    else:
        balance_alert = f'Остаток на балансе: {current_balance}'
    if res:
        await call.message.answer(text=f'Вы успешно записали ребенка на тренировку \n'
                                       f'Имя ребенка: {child_name} \n \n'
                                       f'{call.message.text} \n \n'
                                       f'{balance_alert}', reply_markup=booking_accept_keyboard())
        await call.message.delete()
    else:
        await call.message.answer(text=f'Пополните баланс тренировок \n', reply_markup=booking_accept_keyboard())
        await call.message.delete()


async def booking_cancel_choose(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.booking_cancel_choose)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    trainings_info = await get_child_trainings(child_name)
    trainings_list = []
    for training in trainings_info:
        text = ''
        text += f"{training['date']} "
        text += f"{training['time']} "
        trainings_list.append(text)
    await call.message.answer(text='Выберите тренировку из списка', reply_markup=booking_cancel_choose_keyboard(trainings_list))
    await call.message.delete()


async def booking_cancel_info(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.booking_cancel_confirm)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    trainings_list_of_dict = await get_child_trainings(child_name)
    info = valid_training_date_check(call.data, trainings_list_of_dict)
    await call.message.answer(text=f'Полная информация по тренировке \n'
                                   f'{info}', reply_markup=booking_cancel_info_keyboard())
    await call.message.delete()

async def booking_cancel_confirm(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.booking_cancel_result)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    date_value, time_value = valid_training_message_text(call.message.text)
    res = await child_training_register_delete(child_name, date_value, time_value)
    if res:
        await call.message.answer(text=f'Вы успешно выписали ребёнка с тренировки \n'
                                       f'Имя ребёнка: {child_name}', reply_markup=booking_accept_keyboard())
        await call.message.delete()
    else:
        await call.message.answer(text='Неизвестная ошибка', reply_markup=booking_accept_keyboard())
        await call.message.delete()


async def balance_update(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.update_balance)
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    result = await get_child_balance(child_name)
    user_balance = result[0]['paid_training_count']
    await call.message.answer(text=f'Баланс: {user_balance} \n'
                                   f'Выберите кол-во тренировок для пополнения',
                              reply_markup=update_balance_inline_keyboard())
    await call.message.delete()


async def add_trainings_to_balance(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.add_training_count_choose)
    if call.data[-1] == '2' and call.data[-2] == '1':
        add_trainings_count = '12'
    else:
        add_trainings_count = call.data[-1]
    child_name = await get_child_name(call.message.chat.id, table_name='backend_childid')
    add_trainings_result = await balance_update_db(child_name, int(add_trainings_count))
    date_now = datetime.now()
    date = datetime.date(date_now)
    time = datetime.time(date_now)
    await operation_add_to_story(child_name, date, time, add_trainings_count)
    await call.message.answer(text='Баланс обновлён', reply_markup=back_button())
    await call.message.delete()


async def child_switch(call: CallbackQuery, bot: Bot, state: FSMContext):
    await start(call.message, bot, state)
    await call.message.delete()


async def child_delete_choose(call: CallbackQuery, bot: Bot, state: FSMContext):
    child_names = await get_child_name(call.message.chat.id, table_name='backend_child')
    if isinstance(child_names, str):
        child_names = [child_names]
    await call.message.answer(text='Выберите ребенка, которого хотите удалить', reply_markup=child_names_choosing_keyboard_with_back_button(child_names))
    await state.set_state(MainStates.child_choose_delete)
    await call.message.delete()


async def child_delete(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.child_delete)
    result = await delete_child_remote(call.data)
    await start(call.message, bot, state)
    await call.message.delete()

async def add_child_remote(call: CallbackQuery, bot: Bot, state: FSMContext):
    await cancel(call.message, bot, state)
    await call.message.delete()