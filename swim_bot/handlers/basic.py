from aiogram import Bot
from aiogram.filters import state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.inline import main_menu_inline_keyboard, child_names_choosing_keyboard
from utils.states import MainStates
from utils.commands import set_commands
from database.db_query_funcs import fio_check, parent_exists, parent_id_update, get_child_name, child_name_id_write


async def start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.enter_child_name)
    await set_commands(bot)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except:
        pass
    id_check = await parent_exists(message.chat.id)
    if not id_check:
        await message.answer(text=f'Введите имя и фамилию ребёнка \n \n'
                                  f'Обязательно в формате: \n'
                                  f'Иванов Иван')
        await state.set_state(MainStates.menu_close)
    else:
        child_names = await get_child_name(message.chat.id, table_name='backend_child')
        if isinstance(child_names, str):
            child_names = [child_names]
        await message.answer(text='Выберите ребенка из списка', reply_markup=child_names_choosing_keyboard(child_names))
        await state.set_state(MainStates.child_choose)

async def cancel(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MainStates.enter_child_name)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except:
        pass
    await message.answer(text=f'Введите имя и фамилию ребёнка \n \n'
                        f'Обязательно в формате: \n'
                        f'Иванов Иван')
    await state.set_state(MainStates.menu_close)


async def main_menu_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await parent_id_update(message.chat.id, message.text)
    if current_state == MainStates.menu_close:
        is_format = await fio_check(name=message.text)
        if is_format == True:
            await child_name_id_write(message.chat.id, message.text)
            await message.answer(text='Выберите действие: ', reply_markup=main_menu_inline_keyboard())
            await state.set_state(MainStates.menu_open)
        else:
            await message.answer(text=f'Ребенок не найден.\n'
                                      f'Убедитесь, что написали ФИО в правильном формате или напишите @mvstandard')
    else:
        await message.answer(text='Выберите действие: ', reply_markup=main_menu_inline_keyboard())

