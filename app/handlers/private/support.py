import datetime
import io
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ForumTopic, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from app.filters import IsPrivateChat
from app.handlers.private.start_menu import cmd_menu
from app.keyboards.reply import StartMenuMarkup, BaseReplyMarkup, CancelActionMarkup, EditMessagesMarkup
from app.states.user_states import Support
from app.utils.links import generate_user_link
from app.utils.retry_after import delete_forum_topic_with_retry
from config import MODERATORS_SUPPORT_GROUP_ID, timezone
from database.controllers import MessageToCopyController, SupportSessionController

support_router = Router()
support_router.message.filter(IsPrivateChat())


@support_router.message(F.text == StartMenuMarkup.support)
async def send_support_message(message: Message):
    message_to_copy = await MessageToCopyController.get_message(
        EditMessagesMarkup.support_message
    )
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text="⁉️ View FAQ", callback_data="send_faq")],
        [InlineKeyboardButton(text="📞 Contact Support", callback_data="contact_support")],
    ])
    if not message_to_copy:
        text = (
            f"FAQ"
        )
        await message.answer(
            text=text, reply_markup=builder.as_markup()
        )
    else:
        await message.bot.copy_message(
            from_chat_id=message_to_copy.from_chat_id,
            message_id=message_to_copy.message_id,
            chat_id=message.from_user.id,
            reply_markup=builder.adjust(2).as_markup(),
        )


@support_router.callback_query(F.data == "contact_support")
async def send_support_chat_message(cb: CallbackQuery, state: FSMContext):
    message_to_copy = await MessageToCopyController.get_message(
        EditMessagesMarkup.support_chat_message
    )
    amount = await SupportSessionController.get_sessions_amount()
    if amount > 99:
        user_link = generate_user_link(username=cb.from_user.username, user_id=cb.from_user.id)
        await cb.bot.send_message(text="All operators are currently busy, please try again later.", chat_id=cb.from_user.id)
        await cb.bot.send_message(
            chat_id=MODERATORS_SUPPORT_GROUP_ID,
            message_thread_id=0,
            text=f"User <a href='{user_link}'>{cb.from_user.full_name}</a> tried to connect, "
                 f"but there are too many active sessions at the moment"
        )
        return
    try:
        topic: ForumTopic = await cb.bot.create_forum_topic(chat_id=MODERATORS_SUPPORT_GROUP_ID, name=cb.from_user.full_name)
        message_thread_id = topic.message_thread_id
    except Exception as e:
        logging.warning(e)
        await cb.bot.send_message(chat_id=cb.from_user.id, text="High load, please try again in a few minutes.")
        return
    session = await SupportSessionController.create_session(message_thread_id=message_thread_id, user_id=cb.from_user.id)
    if not message_to_copy:
        text = (
            f"Describe your problem, our specialist will respond to you soon."
        )
        await cb.bot.send_message(
            chat_id=cb.from_user.id, text=text, reply_markup=BaseReplyMarkup().get(buttons=[CancelActionMarkup.cancel])
        )
    else:
        await cb.bot.copy_message(
            from_chat_id=message_to_copy.from_chat_id,
            message_id=message_to_copy.message_id,
            chat_id=cb.from_user.id,
            reply_markup=BaseReplyMarkup().get(buttons=[CancelActionMarkup.cancel])
        )
    await state.set_state(Support.WAITING_MESSAGE)
    await state.update_data({"session_id": session.id})
    user_link = generate_user_link(username=cb.from_user.username, user_id=cb.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="End Session", callback_data=f"close_session:{session.id}")
    )
    new_message = await cb.bot.send_message(
        chat_id=MODERATORS_SUPPORT_GROUP_ID,
        message_thread_id=message_thread_id,
        text=f"<u>User <b><a href='{user_link}'>{cb.from_user.full_name}</a>"
             f" ID {cb.from_user.id}</b> has connected!</u>\n"
             f"/help for help",
        disable_web_page_preview=True,
        reply_markup=builder.as_markup()
    )
    await cb.bot.pin_chat_message(
        chat_id=MODERATORS_SUPPORT_GROUP_ID,
        message_id=new_message.message_id,
    )


@support_router.message(F.text == CancelActionMarkup.cancel, StateFilter(Support.WAITING_MESSAGE))
async def cancel_contact_support(message: Message, state: FSMContext):
    user_link = generate_user_link(username=message.from_user.username, user_id=message.from_user.id)
    data = await state.get_data()
    history = data.get('history', [])
    file_buffer = io.StringIO()
    for msg in history:
        file_buffer.write(f"{msg}\n")

    file_bytes = file_buffer.getvalue().encode('utf-8')
    file = BufferedInputFile(file_bytes, filename="chat_history.txt")
    await message.bot.send_document(
        chat_id=MODERATORS_SUPPORT_GROUP_ID,
        document=file,
        caption=f"Session with <a href='{user_link}'>{message.from_user.full_name}</a> ID {message.from_user.id} has ended."
    )
    session_id = data.get("session_id")
    session = await SupportSessionController.get_session_by_id(session_id=session_id)
    message_thread_id = session.message_thread_id

    await message.bot.send_message(
        chat_id=MODERATORS_SUPPORT_GROUP_ID,
        text=f"<i>User <b><a href='{user_link}'>{message.from_user.full_name}</a>"
             f" ID {message.from_user.id}</b> has disconnected! Ending session...</i>\n",
        message_thread_id=message_thread_id,
        disable_web_page_preview=True
    )
    await cmd_menu(message=message, state=state)
    await SupportSessionController.delete_session(session_id=session_id)
    await delete_forum_topic_with_retry(
        chat_id=MODERATORS_SUPPORT_GROUP_ID,
        message_thread_id=message_thread_id,
        bot=message.bot
    )


@support_router.message(StateFilter(Support.WAITING_MESSAGE))
async def send_user_question(message: Message, state: FSMContext):
    data = await state.get_data()
    session_id = data.get("session_id")
    history = data.get('history', [])
    now = datetime.datetime.now(tz=timezone).strftime("%d.%m.%Y, %H:%M")
    if message.text:
        history.append(f"User {message.from_user.id} {now}: {message.text}")
    elif message.caption:
        history.append(f"User {message.from_user.id} {now} (caption): {message.caption}")

    await state.update_data(history=history)

    session = await SupportSessionController.get_session_by_id(session_id)
    message_thread_id = session.message_thread_id
    try:
        new_message = await message.bot.forward_message(
            chat_id=MODERATORS_SUPPORT_GROUP_ID,
            from_chat_id=message.from_user.id,
            message_id=message.message_id,
            message_thread_id=message_thread_id
        )
    except Exception as e:
        logging.warning(e)
        return
    if not new_message.forward_from:
        builder = InlineKeyboardBuilder([[
            InlineKeyboardButton(text="Reply", callback_data=f"answer_user:{message.from_user.id}")
        ]])
        await message.bot.send_message(
            chat_id=MODERATORS_SUPPORT_GROUP_ID,
            text="Reply via button 👇🏻",
            message_thread_id=message_thread_id,
            reply_markup=builder.as_markup()
        )
