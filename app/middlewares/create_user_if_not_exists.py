from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from database.controllers import UserController
from config import ADMINS_ID


class CreateUserIfNotExistsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        response = await handler(event, data)
        if message := event.message or event.callback_query:
            if isinstance(message, Message):
                if message.chat.type != "private":
                    return response
            else:
                if message.message.chat.type != "private":
                    return response
            tg_user = message.from_user
            tg_id = message.from_user.id
            if tg_id == 777000:
                return response
            user = await UserController.get_user_by_id(int(tg_id))
            if not user:
                is_moderator = str(tg_user.id) in ADMINS_ID
                await UserController.create_new_user(
                    tg_id=tg_user.id,
                    username=tg_user.username,
                    full_name=tg_user.full_name,
                    language_code=tg_user.language_code,
                    is_moderator=is_moderator,
                )
        return response
