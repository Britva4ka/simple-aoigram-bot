from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import Message
from app.filters import IsPrivateChat
from app.keyboards.reply import StartMenuMarkup, EditMessagesMarkup
from database.controllers import SocialMediaController, MessageToCopyController

social_media_router = Router()
social_media_router.message.filter(IsPrivateChat())


@social_media_router.message(F.text == StartMenuMarkup.social_media)
async def send_social_media_message(message: Message):
    social_medias = await SocialMediaController.get_all_social_medias()
    builder = InlineKeyboardBuilder(
        [[
            InlineKeyboardButton(text=social_media.name, url=social_media.url) for social_media in social_medias
        ]]
    )
    message_to_copy = await MessageToCopyController.get_message(
        EditMessagesMarkup.social_media_message
    )

    if not message_to_copy:
        text = (
            f"Click on button, {message.from_user.first_name}"
        )
        await message.answer(
            text=text, reply_markup=builder.adjust(1).as_markup()
        )
    else:
        await message.bot.copy_message(
            from_chat_id=message_to_copy.from_chat_id,
            message_id=message_to_copy.message_id,
            chat_id=message.from_user.id,
            reply_markup=builder.adjust(1).as_markup(),
        )
