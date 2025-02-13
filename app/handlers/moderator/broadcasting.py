import logging

import config
from app.bot import bot
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from app.keyboards.reply import ModeratorMenuMarkup, CancelModeratorActionMarkup
from app.utils.retry_after import copy_message_with_retry
from config import timezone
from database.controllers import UserController
from app.filters import IsModeratorFilter
from app.states.moderator_states import Broadcasting
from app.scheduler import scheduler
from typing import Optional
import datetime


moderator_broadcast_router = Router()
moderator_broadcast_router.message.filter(IsModeratorFilter())


@moderator_broadcast_router.callback_query(F.data == "back_to_broadcast_list")
@moderator_broadcast_router.message(F.text == ModeratorMenuMarkup.list_broadcast)
async def send_broadcast_list(message: Message | CallbackQuery):
    scheduler_jobs = scheduler.get_jobs()
    broadcast_jobs = [job for job in scheduler_jobs if job.id.startswith("broadcast")]
    builder = InlineKeyboardBuilder()
    for job in broadcast_jobs:
        builder.add(
            InlineKeyboardButton(
                text=f"Broadcast scheduled for {job.next_run_time.strftime('%d.%m.%Y %H:%M')}",
                callback_data=f"broadcast:{job.args[0]}:{job.args[1]}:{job.id}",
            )  # job.args[0] - message_id, [1] - chat_id
        )
    if len(broadcast_jobs) < 8:
        builder.adjust(1, repeat=True)
    else:
        builder.adjust(2, repeat=True)
    await message.bot.send_message(
        chat_id=message.from_user.id,
        text="List of scheduled broadcasts:",
        reply_markup=builder.as_markup(),
    )
    if isinstance(message, CallbackQuery):
        await message.message.delete()
        await message.answer()


@moderator_broadcast_router.callback_query(F.data.startswith("broadcast"))
async def show_broadcast_job(cb: CallbackQuery):
    await cb.message.delete()
    _, message_id, chat_id, job_id = cb.data.split(":")
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Cancel broadcast", callback_data=f"remove_broadcast_job:{job_id}"
        ),
        InlineKeyboardButton(
            text="Go back", callback_data="back_to_broadcast_list"
        ),
    )
    await cb.bot.copy_message(
        chat_id=cb.from_user.id,
        from_chat_id=chat_id,
        message_id=message_id,
        reply_markup=builder.as_markup(),
    )
    await cb.answer()


@moderator_broadcast_router.callback_query(F.data.startswith("remove_broadcast_job"))
async def remove_broadcast_job(cb: CallbackQuery):
    _, job_id = cb.data.split(":")
    scheduler.remove_job(job_id=job_id)
    await cb.message.delete()
    await cb.answer("Broadcast canceled", show_alert=True)


@moderator_broadcast_router.message(F.text == ModeratorMenuMarkup.broadcast)
async def ask_broadcast_message(message: Message, state: FSMContext):
    await message.answer(
        "Send me the message for the broadcast",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(Broadcasting.WAIT_BROADCAST_MESSAGE)


@moderator_broadcast_router.message(Broadcasting.WAIT_BROADCAST_MESSAGE)
async def ask_broadcast_button_text(message: Message, state: FSMContext):
    await state.update_data({"message_id": message.message_id})
    await message.answer(
        "Send me the text for the button under the message (or you can add your web app)",
        reply_markup=CancelModeratorActionMarkup().get(buttons=["WEB APP", "Skip"]),
    )
    await state.set_state(Broadcasting.WAIT_BROADCAST_BUTTON_TEXT)


@moderator_broadcast_router.message(
    Broadcasting.WAIT_BROADCAST_BUTTON_TEXT, F.text.in_(["Skip", "WEB APP"])
)
@moderator_broadcast_router.message(Broadcasting.WAIT_BROADCAST_BUTTON_URL)
async def ask_delay(message: Message, state: FSMContext):
    current_state = await state.get_state()
    web_app = False
    if current_state == "Broadcasting:WAIT_BROADCAST_BUTTON_URL":
        await state.update_data({"button_url": message.text.strip()})
    elif current_state == "Broadcasting:WAIT_BROADCAST_BUTTON_TEXT":
        if message.text == "WEB APP":
            web_app = True

    await state.update_data({"web_app": web_app})
    await message.answer(
        "When to start the broadcast? Send me the date in the format: <code>day.month.year hours:minutes</code>!\n"
        "<b>Example: 14.07.2024 22:30</b>\n"
        "<i>(If the broadcast needs to start immediately - send the number</i> <code>0</code>)",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(Broadcasting.WAIT_BROADCAST_DELAY)


@moderator_broadcast_router.message(Broadcasting.WAIT_BROADCAST_BUTTON_TEXT)
async def ask_broadcast_button_url(message: Message, state: FSMContext):
    await state.update_data({"button_text": message.text.strip()})
    await message.answer(
        "Send me the link where the button under the message will lead",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(Broadcasting.WAIT_BROADCAST_BUTTON_URL)


@moderator_broadcast_router.message(Broadcasting.WAIT_BROADCAST_DELAY)
async def start_broadcast(message: Message, state: FSMContext):
    state_data = await state.get_data()
    m_id = int(state_data.get("message_id"))
    btn_text, btn_url = state_data.get("button_text"), state_data.get("button_url")
    button_info = {}
    if btn_text and btn_url:
        button_info["button_text"] = btn_text
        button_info["button_url"] = btn_url

    today = datetime.datetime.now(timezone)
    run_time = today

    if message.text != "0":
        try:
            date, time = message.text.split()
        except ValueError:
            await message.answer("Invalid data format")
            return
        try:
            hour, minute = map(int, time.split(":"))
            day, month, year = map(int, date.split("."))
        except ValueError:
            await message.answer("Invalid data format")
            return
        try:
            start_date = today.replace(
                day=day,
                month=month,
                year=year,
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0,
            )
        except ValueError as e:
            await message.answer(text=f"Error: {e}")
            return

        if start_date < datetime.datetime.now(tz=timezone):
            await message.answer("Broadcast cannot be in the past!")
            return

        run_time = start_date
        await message.answer(
            f"Broadcast scheduled for {time}", reply_markup=ModeratorMenuMarkup().get()
        )
    else:
        await message.answer(
            "Broadcast will start now", reply_markup=ModeratorMenuMarkup().get()
        )
    scheduler.add_job(
        broadcasting,
        "date",
        run_date=run_time,
        args=(m_id, message.from_user.id, button_info, state_data.get("web_app")),
        id=f"broadcast_{m_id}",
    )
    await state.clear()


async def broadcasting(m_id: int, from_user: int, btn_data: Optional[dict], web_app=False):
    messages_sent = 0
    keyboard = None
    if btn_data:
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text=btn_data.get("button_text"), url=btn_data.get("button_url")
            )
        )
        keyboard = builder.as_markup()
    if web_app:
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text=config.WEB_APP_NAME, web_app=WebAppInfo(url=config.WEB_APP_URL)
            )
        )
        keyboard = builder.as_markup()

    await bot.send_message(from_user, "Broadcast started...")
    users_list = await UserController.get_all_users()
    for user in users_list:
        try:
            await copy_message_with_retry(
                bot=bot, user_id=user.tg_id, from_user_id=from_user, message_id=m_id, reply_markup=keyboard
            )
            messages_sent += 1
        except Exception as e:
            logging.error(e)
    await bot.send_message(
        from_user,
        f"Broadcast finished. Total messages sent: <code>{messages_sent}</code>",
    )
