from aiogram import Router, F
from app.filters import IsModeratorFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app.states.moderator_states import FaqMessageForm
from app.keyboards import BaseInlineMarkup
from app.keyboards.reply import (
    CancelModeratorActionMarkup, ModeratorMenuMarkup, FaqMessagesMarkup
)
from database.controllers import FaqMessageController


moderator_faq_router = Router()
moderator_faq_router.message.filter(IsModeratorFilter())


@moderator_faq_router.message(F.text == ModeratorMenuMarkup.edit_faq_messages)
async def send_faq_settings_menu(message: Message):
    faq_messages = await FaqMessageController.get_all_faq_messages()
    text = "FAQ Management Menu, below is the list of active messages:\n\n"
    for faq_message in faq_messages:
        text += f"\n<i>{faq_message.name}</i>"
    await message.answer(
        text=text,
        reply_markup=FaqMessagesMarkup().get(),
        disable_web_page_preview=True
    )


@moderator_faq_router.message(
    F.text == FaqMessagesMarkup.add
)
async def start_creating_faq_message(message: Message, state: FSMContext):
    await message.answer(
        "Enter a name for the button\n",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(FaqMessageForm.WAITING_NAME)


@moderator_faq_router.message(FaqMessageForm.WAITING_NAME)
async def ask_message(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) > 30:
        await message.answer("Name is too long! Enter another one")
        return
    await state.update_data({"name": name})
    await message.answer(
        "Great! Now send the message that will be shown when the button is pressed.",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(FaqMessageForm.WAITING_MESSAGE)


@moderator_faq_router.message(FaqMessageForm.WAITING_MESSAGE)
async def save_new_faq_message(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    try:
        await FaqMessageController.add_faq_message(name=name, chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        await message.answer(f"Error: {e}")
        return
    await message.answer("Successfully added!", reply_markup=FaqMessagesMarkup().get())
    await state.clear()


@moderator_faq_router.message(F.text == FaqMessagesMarkup.delete)
async def choose_faq_to_delete(message: Message):
    faq_messages = await FaqMessageController.get_all_faq_messages()
    markup = BaseInlineMarkup().get(buttons=[(faq.name, f"delete_faq:{faq.name}") for faq in faq_messages])
    await message.answer("Select FAQ to delete:", reply_markup=markup)


@moderator_faq_router.callback_query(F.data.startswith("delete_faq"))
async def delete_faq(cb: CallbackQuery):
    _, name = cb.data.split(":")
    try:
        await FaqMessageController.delete_faq_message(name)
    except Exception as e:
        await cb.bot.send_message(chat_id=cb.from_user.id, text=f"Error: {e}")
        return
    faq_messages = await FaqMessageController.get_all_faq_messages()
    markup = BaseInlineMarkup().get(buttons=[(faq.name, f"delete_faq:{faq.name}") for faq in faq_messages])
    await cb.message.edit_reply_markup(reply_markup=markup)
    await cb.answer("Successfully deleted", show_alert=True)
