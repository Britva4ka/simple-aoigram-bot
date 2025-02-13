from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from app.filters import IsPrivateChat, StateGroupFilter
from app.keyboards.inline import FeedbackMarkup, CancelActionInlineMarkup, AnonymousMarkup
from app.keyboards.reply import StartMenuMarkup, EditMessagesMarkup
from app.states.user_states import Feedback
from app.utils.links import generate_user_link
from database.controllers import MessageToCopyController, FeedbackController, UserController
from config import MODERATORS_FEEDBACK_GROUP_ID

feedback_router = Router()
feedback_router.message.filter(IsPrivateChat())


@feedback_router.message(F.text == StartMenuMarkup.feedback)
async def send_feedback_message(message: Message | CallbackQuery):
    message_to_copy = await MessageToCopyController.get_message(
        EditMessagesMarkup.feedback_message
    )
    markup = FeedbackMarkup().get(row_size=1)
    if not message_to_copy:
        text = (
            f"Feedback menu, are we looking or leaving feedback, {message.from_user.first_name}?"
        )
        await message.bot.send_message(
            chat_id=message.from_user.id, text=text, reply_markup=markup
        )
    else:
        await message.bot.copy_message(
            from_chat_id=message_to_copy.from_chat_id,
            message_id=message_to_copy.message_id,
            chat_id=message.from_user.id,
            reply_markup=markup
        )
    if isinstance(message, CallbackQuery):
        await message.answer()


@feedback_router.callback_query(F.data == FeedbackMarkup.view_feedback[-1])
async def view_feedback(cb: CallbackQuery, page: int = 1):
    feedbacks = await FeedbackController().get_feedbacks_page(page=page, per_page=4)
    next_page = await FeedbackController().get_feedbacks_page(page=page+1, per_page=4)
    total_feedbacks = len(feedbacks)

    builder = InlineKeyboardBuilder()

    # Add feedbacks: maximum 2 per row
    for i in range(0, total_feedbacks, 2):
        user = await UserController.get_user_by_id(feedbacks[i].author_id)
        if feedbacks[i].is_anonymous:
            title = "Anonymous"
        else:
            title = f"@{user.username}" if user.username else user.full_name
        row = [
            InlineKeyboardButton(text=title, callback_data=f"show_fb:{feedbacks[i].id}")
        ]
        if i + 1 < total_feedbacks:
            user = await UserController.get_user_by_id(feedbacks[i + 1].author_id)
            if feedbacks[i + 1].is_anonymous:
                title = "Anonymous"
            else:
                title = f"@{user.username}" if user.username else user.full_name
            row.append(
                InlineKeyboardButton(text=title, callback_data=f"show_fb:{feedbacks[i + 1].id}")
            )
        builder.row(*row)

    # Navigation buttons (left/right)
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"fb_page:{page - 1}"))
    if next_page:  # If there is a next page
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"fb_page:{page + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)

    # Back button
    builder.row(InlineKeyboardButton(text="↩️ Back", callback_data="fb_back"))
    await cb.message.edit_reply_markup(reply_markup=builder.as_markup())
    await cb.answer()


@feedback_router.callback_query(F.data.startswith("show_fb"))
async def show_fb(cb: CallbackQuery):
    user = await UserController.get_user_by_id(cb.from_user.id)

    _, feedback_id = cb.data.split(":")
    feedback = await FeedbackController.get_feedback_by_id(int(feedback_id))
    if feedback.is_anonymous:
        await cb.bot.copy_message(
            chat_id=cb.from_user.id,
            from_chat_id=feedback.chat_id,
            message_id=feedback.message_id
        )
    else:
        await cb.bot.forward_message(
            chat_id=cb.from_user.id,
            from_chat_id=feedback.chat_id,
            message_id=feedback.message_id
        )

    if user.is_moderator:
        builder = InlineKeyboardBuilder()
        if not feedback.is_pinned:
            builder.add(InlineKeyboardButton(text="Pin", callback_data=f"pin_fb:{feedback.id}"))
        else:
            builder.add(InlineKeyboardButton(text="Unpin", callback_data=f"unpin_fb:{feedback_id}"))
        builder.add(InlineKeyboardButton(text="Unpublish", callback_data=f"delete_fb:{feedback.id}"))
        await cb.bot.send_message(
            chat_id=cb.from_user.id,
            text="You are a moderator and can interact with this feedback",
            reply_markup=builder.adjust(1, 1).as_markup()
        )
    await cb.answer()


@feedback_router.callback_query(F.data.startswith("fb_page"))
async def paginate_fb(cb: CallbackQuery):
    _, page = cb.data.split(":")
    await view_feedback(cb=cb, page=int(page))


@feedback_router.callback_query(F.data == "fb_back")
async def back_to_fb_menu(cb: CallbackQuery):
    await cb.message.edit_reply_markup(reply_markup=FeedbackMarkup().get(row_size=1))
    await cb.answer()


@feedback_router.callback_query(F.data == FeedbackMarkup.leave_feedback[-1])
async def leave_feedback(cb: CallbackQuery, state: FSMContext):
    markup = AnonymousMarkup().get(row_size=2)
    text = "Do you want to leave feedback anonymously or not?"
    await state.set_state(Feedback.WAITING_ANONYMOUS)
    if cb.message.text:
        await cb.message.edit_text(text=text, reply_markup=markup)
    else:
        await cb.message.edit_caption(caption=text, reply_markup=markup)
    await cb.answer()


@feedback_router.callback_query(StateFilter(Feedback.WAITING_ANONYMOUS), F.data.startswith("anonymous"))
async def ask_feedback(cb: CallbackQuery, state: FSMContext):
    callback_data = cb.data.split(":")[-1]
    text = "Send me your feedback"
    await state.set_state(Feedback.WAITING_MESSAGE)
    await state.update_data({"anonymous": callback_data})
    markup = CancelActionInlineMarkup().get()
    if cb.message.text:
        await cb.message.edit_text(text=text, reply_markup=markup)
    else:
        await cb.message.edit_caption(caption=text, reply_markup=markup)
    await cb.answer()


@feedback_router.message(StateFilter(Feedback.WAITING_MESSAGE))
async def process_feedback(message: Message, state: FSMContext):
    data = await state.get_data()
    anonymous = data.get("anonymous")
    await state.clear()
    callback = f"confirm_fb:{message.from_user.id}:{message.message_id}:{anonymous}"
    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text="Publish feedback", callback_data=callback)]])
    user_link = generate_user_link(username=message.from_user.username, user_id=message.from_user.id)
    await message.bot.send_message(
        chat_id=MODERATORS_FEEDBACK_GROUP_ID,
        text=f"<b><u>NEW FEEDBACK RECEIVED</u></b>\n"
             f"Author: <a href='{user_link}'>{message.from_user.full_name}</a>\n"
             f"ID: {message.from_user.id} - {'Anonymous' if anonymous=='true' else 'Not Anonymous'}\n"
             f"To call for help /help\n"
             f"_________________",
        disable_web_page_preview=True
    )
    await message.bot.copy_message(
        chat_id=MODERATORS_FEEDBACK_GROUP_ID,
        from_chat_id=message.from_user.id,
        message_id=message.message_id,
        reply_markup=builder.as_markup()
    )
    await message.answer("Your feedback has been saved, thank you!")
    await send_feedback_message(message)


@feedback_router.callback_query(StateGroupFilter(Feedback), F.data == CancelActionInlineMarkup.cancel[-1])
async def cancel_feedback(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()
    await send_feedback_message(cb)
    await cb.answer()
