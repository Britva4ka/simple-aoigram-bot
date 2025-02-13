from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from app.filters import IsModeratorFilter, IsModeratorsFeedbackChat

from database.controllers import FeedbackController

moderators_feedback_router = Router()
moderators_feedback_router.message.filter(IsModeratorFilter())
moderators_feedback_router.callback_query.filter(IsModeratorFilter())


@moderators_feedback_router.message(Command('help'), IsModeratorsFeedbackChat())
async def help_message(message: Message):
    await message.answer(
        text="<b>This is a chat for moderators where feedback from users will be received.</b>\n\n"
             "<i>When a user leaves feedback, you will receive a notification with a button to confirm its publication."
             "After confirmation, the feedback can be pinned as one of the first ones, and all actions can be undone."
             "\n\nThe bot will forward user messages. You will see their ID and a link to their account."
             "That is, if necessary, you will be able to contact them.</i>\n\n"
             "You can also interact with feedback directly in the bot if you happen to lose one in the chat."
    )


@moderators_feedback_router.callback_query(F.data.startswith("confirm_fb"))
async def confirm_fb(cb: CallbackQuery):
    _, user_id, message_id, anonymous = cb.data.split(":")
    anonymous = True if anonymous == 'true' else False
    feedback = await FeedbackController.create_feedback(
        chat_id=int(user_id),
        message_id=int(message_id),
        author_id=int(user_id),
        approver_id=int(cb.from_user.id),
        is_anonymous=anonymous
    )
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Pin", callback_data=f"pin_fb:{feedback.id}"))
    builder.add(InlineKeyboardButton(text="Cancel publication", callback_data=f"delete_fb:{feedback.id}"))
    await cb.message.edit_reply_markup(reply_markup=builder.adjust(1, 1).as_markup())
    await cb.answer()


@moderators_feedback_router.callback_query(F.data.startswith("pin_fb"))
async def pin_fb(cb: CallbackQuery):
    _, feedback_id = cb.data.split(":")
    await FeedbackController.pin_feedback_by_id(feedback_id=int(feedback_id))
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Unpin", callback_data=f"unpin_fb:{feedback_id}"))
    builder.add(InlineKeyboardButton(text="Cancel publication", callback_data=f"delete_fb:{feedback_id}"))
    await cb.message.edit_reply_markup(reply_markup=builder.adjust(1, 1).as_markup())
    await cb.answer()


@moderators_feedback_router.callback_query(F.data.startswith("unpin_fb"))
async def unpin_fb(cb: CallbackQuery):
    _, feedback_id = cb.data.split(":")
    await FeedbackController.unpin_feedback_by_id(feedback_id=int(feedback_id))
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Pin", callback_data=f"pin_fb:{feedback_id}"))
    builder.add(InlineKeyboardButton(text="Cancel publication", callback_data=f"delete_fb:{feedback_id}"))
    await cb.message.edit_reply_markup(reply_markup=builder.adjust(1, 1).as_markup())
    await cb.answer()


@moderators_feedback_router.callback_query(F.data.startswith("delete_fb"))
async def delete_fb(cb: CallbackQuery):
    _, feedback_id = cb.data.split(":")
    feedback = await FeedbackController.get_feedback_by_id(feedback_id=int(feedback_id))
    if feedback:
        user_id = feedback.author_id
        message_id = feedback.message_id
        anonymous = "true" if feedback.is_anonymous else 'false'
        await FeedbackController.delete_feedback_by_id(feedback_id=int(feedback_id))
        callback = f"confirm_fb:{user_id}:{message_id}:{anonymous}"
        builder = InlineKeyboardBuilder([[InlineKeyboardButton(text="Publish feedback", callback_data=callback)]])
        await cb.message.edit_reply_markup(reply_markup=builder.as_markup())
    await cb.answer()
