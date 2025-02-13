from aiogram import BaseMiddleware
from aiogram.types import Update
from database.controllers import UserController, MessageToCopyController
from app.keyboards.reply import EditMessagesMarkup
from config import ADMINS_ID


class UserIsBannedMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        else:
            return await handler(event, data)
        user = await UserController.get_user_by_id(user_id)
        if user and user.is_banned and str(user.tg_id) not in ADMINS_ID:
            ban_message = await MessageToCopyController.get_message(
                EditMessagesMarkup.ban_message
            )
            if ban_message:
                await event.bot.copy_message(
                    chat_id=event.from_user.id,
                    message_id=ban_message.message_id,
                    from_chat_id=ban_message.from_chat_id,
                )
                return
            else:
                await event.bot.send_message(chat_id=user_id, text="You are blocked.")
                return
        return await handler(event, data)
