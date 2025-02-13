from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.keyboards.reply import (
    ModeratorMenuMarkup,
    CancelModeratorActionMarkup,
)
from app.filters import IsModeratorFilter
from database.controllers import UserController

moderator_menu_router = Router()
moderator_menu_router.message.filter(IsModeratorFilter())


@moderator_menu_router.message(Command("moder"))
async def send_moderator_menu(message: Message, state: FSMContext):
    user = await UserController.get_user_by_id(int(message.from_user.id))
    if not user.is_moderator:
        await UserController.switch_user_moderator(int(message.from_user.id))
    await state.clear()
    await message.answer("Moderator panel:", reply_markup=ModeratorMenuMarkup().get())


@moderator_menu_router.message(F.text == CancelModeratorActionMarkup.cancel)
async def cancel_moderator_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Canceled", reply_markup=ModeratorMenuMarkup().get())
