from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    TOGGLE_BAN = State()
    TOGGLE_MODER = State()
