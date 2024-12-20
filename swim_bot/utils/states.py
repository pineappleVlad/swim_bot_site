from aiogram.fsm.state import StatesGroup, State


class MainStates(StatesGroup):
    start = State()
    enter_child_name = State()
    child_choose = State()
    menu_open = State()
    menu_close = State()
    view_stats = State()
    view_balance = State()
    choose_pool_type_state = State()
    choose_trainer_state = State()
    choose_training_date = State()
    confirm_booking = State()
    booking_accept = State()
    booking_cancel_choose = State()
    booking_cancel_confirm = State()
    booking_cancel_result = State()
    update_balance = State()
    add_training_count_choose = State()
    child_choose_delete = State()
    child_delete = State()


