import datetime
import io
import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from aiogram.filters.state import StateFilter
from aiogram.filters.command import Command
from app.bot import dp
from app.states.moderator_states import AnswerUser
from app.filters import IsGroupChat, IsModeratorFilter, IsModeratorsSupportChat
from app.keyboards.reply import StartMenuMarkup, BaseReplyMarkup, CancelActionMarkup
from app.utils.links import generate_user_link
from app.utils.retry_after import delete_forum_topic_with_retry
from config import MODERATORS_SUPPORT_GROUP_ID, timezone
from database.controllers import SupportSessionController, UserController

moderators_support_router = Router()
moderators_support_router.message.filter(IsGroupChat(), IsModeratorFilter(), IsModeratorsSupportChat())
moderators_support_router.callback_query.filter(IsGroupChat(), IsModeratorFilter(), IsModeratorsSupportChat())


@moderators_support_router.message(Command('help'))
async def help_message(message: Message):
    await message.answer(
        text="<b>This is a chat for moderators where requests from users will be received.</b>\n\n"
             "<i>When a user connects, a topic will be created with them, and you will receive a notification, "
             "which will also include a link to their profile and their ID.\n\n"
             "The bot will forward user messages. To reply anonymously via the bot, just reply to the forwarded "
             "message in this thread, and the bot will send it from its own name.\n\n"
             "IMPORTANT! Some users may only be able to respond via the button (when their profile is hidden during forwarding)."
             "In that case, replying to the message will not work, you must press the button.</i><u>\n\n"
             "Messages sent that are not replies to a message and not through the 'Reply' button will not be received by the user.\n\n"
             "</u>Chat histories will be sent to the GENERAL thread, and the maximum number of active sessions is 100."
    )


@moderators_support_router.message(F.reply_to_message.forward_from)
async def reply_forwarder(message: Message):
    original_author_id = message.reply_to_message.forward_from.id
    state_with: FSMContext = FSMContext(
        storage=dp.storage,
        key=StorageKey(
            chat_id=original_author_id,
            user_id=original_author_id,
            bot_id=message.bot.id))
    data = await state_with.get_data()
    history = data.get('history', [])
    now = datetime.datetime.now(tz=timezone).strftime("%d.%m.%Y, %H:%M")
    if message.text:
        history.append(f"Moderator {message.from_user.id} {now}: {message.text}")

    elif message.caption:
        history.append(f"Moderator {message.from_user.id} {now} (caption): {message.caption}")

    await state_with.update_data(history=history)

    try:
        await message.bot.copy_message(
            chat_id=original_author_id,
            message_id=message.message_id,
            from_chat_id=message.chat.id,
        )
    except Exception as e:
        await message.reply(text=f"Error: {e}")
        return
    await message.reply(text=f"User {message.reply_to_message.forward_from.full_name} received your response.")


@moderators_support_router.callback_query(F.data.startswith("answer_user"))
async def ask_answer_for_user(callback: CallbackQuery, state: FSMContext):
    _, user_id = callback.data.split(":")
    await state.set_state(AnswerUser.WAIT_FOR_ANSWER_FOR_USER)
    await state.update_data(
        {"user_id": user_id}
    )
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        message_thread_id=callback.message.message_thread_id,
        text=f"{callback.from_user.full_name}, awaiting your response.",
        reply_markup=BaseReplyMarkup().get(buttons=[CancelActionMarkup.cancel])
    )
    await callback.answer()


@moderators_support_router.message(F.text == CancelActionMarkup.cancel, StateFilter(AnswerUser.WAIT_FOR_ANSWER_FOR_USER))
async def cancel_answer_user(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Cancelled", reply_markup=ReplyKeyboardRemove())


@moderators_support_router.message(StateFilter(AnswerUser.WAIT_FOR_ANSWER_FOR_USER))
async def answer_user(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    user_id = data.get("user_id")
    state_with: FSMContext = FSMContext(
        storage=dp.storage,
        key=StorageKey(
            chat_id=user_id,
            user_id=user_id,
            bot_id=message.bot.id))
    data = await state_with.get_data()
    history = data.get('history', [])
    now = datetime.datetime.now(tz=timezone).strftime("%d.%m.%Y, %H:%M")
    if message.text:
        history.append(f"Moderator {message.from_user.id} {now}: {message.text}")
        logging.warning(now)

    elif message.caption:
        history.append(f"Moderator {message.from_user.id} {now} (caption): {message.caption}")

    await state_with.update_data(history=history)

    try:
        await message.bot.copy_message(from_chat_id=message.chat.id, message_id=message.message_id, chat_id=user_id)
    except Exception as e:
        await message.reply(text=f"Error: {e}")
        return
    user_chat = await message.bot.get_chat(chat_id=user_id)
    await message.reply(text=f"User {user_chat.full_name} received your response.",
                        reply_markup=ReplyKeyboardRemove())


@moderators_support_router.callback_query(F.data.startswith("close_session"))
async def close_support_session(cb: CallbackQuery):
    _, session_id = cb.data.split(":")
    session = await SupportSessionController.get_session_by_id(session_id=int(session_id))
    message_thread_id = session.message_thread_id
    state_with: FSMContext = FSMContext(
        storage=dp.storage,
        key=StorageKey(
            chat_id=session.user_id,
            user_id=session.user_id,
            bot_id=cb.bot.id))
    data = await state_with.get_data()
    history = data.get('history', [])
    file_buffer = io.StringIO()
    for msg in history:
        file_buffer.write(f"{msg}\n")

    file_bytes = file_buffer.getvalue().encode('utf-8')
    file = BufferedInputFile(file_bytes, filename="chat_history.txt")
    user = await UserController.get_user_by_id(tg_id=session.user_id)
    user_link = generate_user_link(username=user.username, user_id=user.tg_id)
    await cb.bot.send_document(
        chat_id=MODERATORS_SUPPORT_GROUP_ID,
        document=file,
        caption=f"Session with <a href='{user_link}'>{user.full_name}</a> ID {user.tg_id} has been completed."
    )

    await state_with.clear()
    await cb.bot.send_message(
        chat_id=session.user_id,
        text="The operator has ended the session",
        reply_markup=StartMenuMarkup().get(row_size=[1, 2, 1])
    )
    await SupportSessionController.delete_session(session_id=session_id)
    await delete_forum_topic_with_retry(
        chat_id=MODERATORS_SUPPORT_GROUP_ID,
        message_thread_id=message_thread_id,
        bot=cb.bot
    )
