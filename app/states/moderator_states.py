from aiogram.fsm.state import StatesGroup, State


class EditMessage(StatesGroup):
    WAITING_MESSAGE = State()


class Broadcasting(StatesGroup):
    WAIT_BROADCAST_MESSAGE = State()
    WAIT_BROADCAST_BUTTON_TEXT = State()
    WAIT_BROADCAST_BUTTON_URL = State()
    WAIT_BROADCAST_DELAY = State()


class AnswerUser(StatesGroup):
    WAIT_FOR_ANSWER_FOR_USER = State()


class SocialMediaForm(StatesGroup):
    WAITING_NAME = State()
    WAITING_URL = State()


class FaqMessageForm(StatesGroup):
    WAITING_NAME = State()
    WAITING_MESSAGE = State()
