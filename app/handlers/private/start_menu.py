from aiogram import Router
from aiogram.filters import Command, CommandObject, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import Message, ChatMemberUpdated
from aiogram.fsm.context import FSMContext
from app.filters import IsPrivateChat
from app.keyboards.reply import StartMenuMarkup, EditMessagesMarkup
from config import ADMINS_ID
from database.controllers import UserController, MessageToCopyController

start_menu_router = Router()
start_menu_router.message.filter(IsPrivateChat())


@start_menu_router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()
    tg_user = message.from_user
    # Checking arguments /start
    # args = None
    # if command:
    #     args = command.args

    db_user = await UserController.get_user_by_id(tg_id=tg_user.id)
    if not db_user:
        is_moderator = str(tg_user.id) in ADMINS_ID
        await UserController.create_new_user(
            tg_id=tg_user.id,
            username=tg_user.username,
            full_name=tg_user.full_name,
            language_code=tg_user.language_code,
            is_moderator=is_moderator,
        )
    await cmd_menu(message, state)


@start_menu_router.message(Command(commands=["menu"]))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    message_to_copy = await MessageToCopyController.get_message(
        EditMessagesMarkup.main_menu_message
    )
    if not message_to_copy:
        text = (
            f"Hello, {message.from_user.first_name}"
        )
        await message.answer(
            text=text, reply_markup=StartMenuMarkup().get(row_size=[1, 2, 1])
        )
    else:
        await message.bot.copy_message(
            from_chat_id=message_to_copy.from_chat_id,
            message_id=message_to_copy.message_id,
            chat_id=message.from_user.id,
            reply_markup=StartMenuMarkup().get(row_size=[1, 2, 1]),
        )


@start_menu_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    await UserController.mark_bot_as_banned(event.from_user.id)


@start_menu_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    await UserController.mark_bot_as_unbanned(event.from_user.id)
