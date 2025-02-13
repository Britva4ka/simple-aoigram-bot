from aiogram.fsm.state import StatesGroup, State


class Support(StatesGroup):
    WAITING_MESSAGE = State()


class Feedback(StatesGroup):
    WAITING_ANONYMOUS = State()
    WAITING_MESSAGE = State()
