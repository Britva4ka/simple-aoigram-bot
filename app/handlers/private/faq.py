from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from app.filters import IsPrivateChat
from app.keyboards.reply import StartMenuMarkup, EditMessagesMarkup
from database.controllers import FaqMessageController, MessageToCopyController

faq_message_router = Router()
faq_message_router.message.filter(IsPrivateChat())


@faq_message_router.callback_query(F.data == "send_faq")
@faq_message_router.message(F.text == StartMenuMarkup.faq)
async def send_faq_message(message: Message | CallbackQuery):
    faq_messages = await FaqMessageController.get_all_faq_messages()
    builder = InlineKeyboardBuilder(
        [[
            InlineKeyboardButton(
                text=faq_message.name,
                callback_data=f"show_faq:{faq_message.chat_id}:{faq_message.message_id}")
            for faq_message in faq_messages
        ]]
    )
    message_to_copy = await MessageToCopyController.get_message(
        EditMessagesMarkup.faq_message
    )

    if not message_to_copy:
        text = (
            f"Choose the interesting one, {message.from_user.first_name}"
        )
        await message.bot.send_message(
            chat_id=message.from_user.id, text=text, reply_markup=builder.adjust(1).as_markup()
        )
    else:
        await message.bot.copy_message(
            from_chat_id=message_to_copy.from_chat_id,
            message_id=message_to_copy.message_id,
            chat_id=message.from_user.id,
            reply_markup=builder.adjust(1).as_markup(),
        )
    if isinstance(message, CallbackQuery):
        await message.answer()


@faq_message_router.callback_query(F.data.startswith("show_faq"))
async def show_faq(cb: CallbackQuery):
    _, chat_id, message_id = cb.data.split(":")
    faq_messages = await FaqMessageController.get_all_faq_messages()
    builder = InlineKeyboardBuilder(
        [[
            InlineKeyboardButton(
                text=faq_message.name,
                callback_data=f"show_faq:{faq_message.chat_id}:{faq_message.message_id}")
            for faq_message in faq_messages
        ]]
    )
    await cb.message.delete()
    await cb.bot.copy_message(
        from_chat_id=chat_id,
        chat_id=cb.from_user.id,
        message_id=message_id,
        reply_markup=builder.adjust(1).as_markup()
    )
    await cb.answer()
