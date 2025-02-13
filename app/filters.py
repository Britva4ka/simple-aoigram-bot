from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.controllers.user import UserController
from config import ADMINS_ID, MODERATORS_SUPPORT_GROUP_ID, MODERATORS_FEEDBACK_GROUP_ID


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        return str(message.from_user.id) in ADMINS_ID


class IsModeratorFilter(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:

        user = await UserController.get_user_by_id(int(message.from_user.id))
        if not user:
            return False
        return user.is_moderator or str(message.from_user.id) in ADMINS_ID


class IsPrivateChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type == "private"


class IsGroupChat(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        if isinstance(message, Message):
            chat_type = message.chat.type
        else:
            chat_type = message.message.chat.type
        return chat_type in ["group", "supergroup"]


class IsModeratorsSupportChat(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        if isinstance(message, Message):
            chat_id = message.chat.id
        else:
            chat_id = message.message.chat.id
        return str(chat_id) == MODERATORS_SUPPORT_GROUP_ID


class IsModeratorsFeedbackChat(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        if isinstance(message, Message):
            chat_id = message.chat.id
        else:
            chat_id = message.message.chat.id
        return str(chat_id) == MODERATORS_FEEDBACK_GROUP_ID


class IsChannelChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type == "channel"


class StateGroupFilter(BaseFilter):
    def __init__(self, *state_groups):
        self.state_groups = state_groups

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        if current_state:
            for group in self.state_groups:
                if current_state.startswith(group.__name__):
                    return True
        return False
