from aiogram import Router, F
from app.filters import IsModeratorFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.states.moderator_states import EditMessage
from app.keyboards.reply import (
    ModeratorMenuMarkup,
    EditMessagesMarkup,
    CancelModeratorActionMarkup,
)
from database.controllers import MessageToCopyController


moderator_messages_router = Router()
moderator_messages_router.message.filter(IsModeratorFilter())
messages_buttons_list = EditMessagesMarkup().get_buttons_list_from_attributes()


@moderator_messages_router.message(F.text == ModeratorMenuMarkup.edit_messages)
async def send_messages_settings_menu(message: Message):
    await message.answer(
        "You are in the settings menu for pre-made messages that do not require any data input\n\n"
        "<i>The working principle is copying. You can send any message with photo/video, etc. "
        "or without any content at all</i>",
        reply_markup=EditMessagesMarkup().get(),
    )


@moderator_messages_router.message(F.text.in_(messages_buttons_list))
async def ask_new_message(message: Message, state: FSMContext):
    await message.answer(
        text=f"Send the new message you want to use for {message.text}",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(EditMessage.WAITING_MESSAGE)
    await state.update_data({"key": message.text})


@moderator_messages_router.message(EditMessage.WAITING_MESSAGE)
async def save_new_message(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("key")
    chat_id = message.from_user.id
    message_id = message.message_id
    message_from_db = await MessageToCopyController.get_message(key=key)
    if message_from_db:
        await MessageToCopyController.update_message(
            key=key, new_message_id=message_id, new_from_chat_id=chat_id
        )
    else:
        await MessageToCopyController.add_message(
            key=key, message_id=message_id, from_chat_id=chat_id
        )
    await message.answer("Successfully updated!", reply_markup=ModeratorMenuMarkup().get())
    await state.clear()
