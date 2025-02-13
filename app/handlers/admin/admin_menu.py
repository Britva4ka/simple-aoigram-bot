from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.keyboards.reply import AdminMenuMarkup, CancelAdminActionMarkup
from app.keyboards import BaseInlineMarkup
from app.filters import IsAdminFilter
from app.states.admin_states import AdminStates
from database.controllers import UserController
from config import ADMINS_ID

admin_menu_router = Router()
admin_menu_router.message.filter(IsAdminFilter())
admin_menu_router.callback_query.filter(IsAdminFilter())


@admin_menu_router.message(Command("admin"))
async def send_admin_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Admin panel:", reply_markup=AdminMenuMarkup().get())


@admin_menu_router.message(F.text == CancelAdminActionMarkup.cancel)
async def cancel_admin_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Canceled", reply_markup=AdminMenuMarkup().get())


@admin_menu_router.message(F.text == AdminMenuMarkup.ban_list)
async def send_ban_list(message: Message | CallbackQuery, page: int = 1):
    text = "Ban List\n"
    banned_users = await UserController.get_banned_users_by_page(page=page)
    next_page = await UserController.get_banned_users_by_page(page=page + 1)
    for user in banned_users:
        text += f"{user.tg_id} {user.full_name}\n"
    buttons = []
    if page > 1:
        buttons.append(("Back", f"banned_users:{page - 1}"))
    if next_page:
        buttons.append(("further", f"banned_users:{page + 1}"))
    keyboard = BaseInlineMarkup().get(buttons=buttons)
    if isinstance(message, Message):
        await message.answer(text=text, reply_markup=keyboard)
    else:
        await message.message.edit_text(text=text, reply_markup=keyboard)


@admin_menu_router.callback_query(F.data.startswith("banned_users"))
async def handle_banned_users_pagination(cb: CallbackQuery):
    page = int(cb.data.split(":")[-1])
    await send_ban_list(cb, page)


@admin_menu_router.message(F.text == AdminMenuMarkup.moderators_list)
async def send_moderator_list(message: Message | CallbackQuery, page: int = 1):
    text = "Moderators list\n"
    moderators = await UserController.get_moderators_by_page(page=page)
    next_page = await UserController.get_moderators_by_page(page=page + 1)
    for moderator in moderators:
        text += f"{moderator.tg_id} {moderator.full_name}\n"
    buttons = []
    if page > 1:
        buttons.append(("Back", f"moderators:{page - 1}"))
    if next_page:
        buttons.append(("Further", f"moderators:{page + 1}"))
    keyboard = BaseInlineMarkup().get(buttons=buttons)
    if isinstance(message, Message):
        await message.answer(text=text, reply_markup=keyboard)
    else:
        await message.message.edit_text(text=text, reply_markup=keyboard)


@admin_menu_router.callback_query(F.data.startswith("moderators"))
async def handle_moderators_pagination(cb: CallbackQuery):
    page = int(cb.data.split(":")[-1])
    await send_moderator_list(cb, page)


@admin_menu_router.message(F.text == AdminMenuMarkup.switch_ban)
async def ask_tg_id_to_ban(message: Message, state: FSMContext):
    await state.set_state(AdminStates.TOGGLE_BAN)
    await message.answer(
        "Enter telegram id of user, which status will be changed",
        reply_markup=CancelAdminActionMarkup().get(),
    )


@admin_menu_router.message(AdminStates.TOGGLE_BAN)
async def switch_user_ban(message: Message, state: FSMContext):
    answer = message.text.strip()
    try:
        tg_id = int(answer)
    except ValueError:
        await message.answer("Telegram id must be integer")
        return
    user = await UserController.get_user_by_id(tg_id=tg_id)
    if user.tg_id in ADMINS_ID:
        await message.answer("Good luck, boy :)")
        return
    result = await UserController.switch_user_ban(tg_id=tg_id)
    if not result:
        await message.answer("User not found")
        return
    user = await UserController.get_user_by_id(tg_id=tg_id)
    await message.answer(
        f"Status of {user.full_name} had been changed to"
        f" {'<b>banned</b>' if user.is_banned else '<b>unbanned</b>'}",
        reply_markup=AdminMenuMarkup().get(),
    )
    await state.clear()


@admin_menu_router.message(F.text == AdminMenuMarkup.switch_moderator)
async def ask_tg_id_to_make_moderator(message: Message, state: FSMContext):
    await state.set_state(AdminStates.TOGGLE_MODER)
    await message.answer(
        "Enter telegram id of user, which status will be changed",
        reply_markup=CancelAdminActionMarkup().get(),
    )


@admin_menu_router.message(AdminStates.TOGGLE_MODER)
async def switch_user_moderator(message: Message, state: FSMContext):
    answer = message.text.strip()
    try:
        tg_id = int(answer)
    except ValueError:
        await message.answer("Telegram id must be integer")
        return
    result = await UserController.switch_user_moderator(tg_id=tg_id)
    if not result:
        await message.answer("User not found")
        return
    user = await UserController.get_user_by_id(tg_id=tg_id)
    await message.answer(
        f"Status of {user.full_name} has been changed to"
        f" {'<b>moderator</b>' if user.is_moderator else '<b>not moderator</b>'}",
        reply_markup=AdminMenuMarkup().get(),
    )
    await state.clear()
