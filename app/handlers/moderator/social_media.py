from aiogram import Router, F
from app.filters import IsModeratorFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app.states.moderator_states import SocialMediaForm
from app.keyboards import BaseInlineMarkup
from app.keyboards.reply import (
    CancelModeratorActionMarkup,
    SocialMediasMarkup, ModeratorMenuMarkup,
)
from app.utils.links import is_valid_url
from database.controllers import SocialMediaController


moderator_social_medias_router = Router()
moderator_social_medias_router.message.filter(IsModeratorFilter())


@moderator_social_medias_router.message(F.text == ModeratorMenuMarkup.edit_social_medias)
async def send_messages_settings_menu(message: Message):
    social_medias = await SocialMediaController.get_all_social_medias()
    text = "Social media management menu, below is the list of active ones:\n\n"
    for social_media in social_medias:
        text += f"\n<i>{social_media.name} - {social_media.url}</i>"
    await message.answer(
        text=text,
        reply_markup=SocialMediasMarkup().get(),
        disable_web_page_preview=True
    )


@moderator_social_medias_router.message(
    F.text == SocialMediasMarkup.add
)
async def start_creating_social_media(message: Message, state: FSMContext):
    await message.answer(
        "Enter the social media name\n",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(SocialMediaForm.WAITING_NAME)


@moderator_social_medias_router.message(SocialMediaForm.WAITING_NAME)
async def ask_url(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) > 30:
        await message.answer("The name is too long! Please enter another one")
        return
    await state.update_data({"name": name})
    await message.answer(
        "Great! Now send the link to the social media",
        reply_markup=CancelModeratorActionMarkup().get(),
    )
    await state.set_state(SocialMediaForm.WAITING_URL)


@moderator_social_medias_router.message(SocialMediaForm.WAITING_URL)
async def save_new_social_media(message: Message, state: FSMContext):
    url = message.text.strip()
    if not is_valid_url(url):
        await message.answer("The link is incorrect, try another one")
        return

    data = await state.get_data()
    name = data.get("name")
    try:
        await SocialMediaController.add_social_media(name, url)
    except Exception as e:
        await message.answer(f"Error: {e}")
        return
    await message.answer("Successfully added!", reply_markup=SocialMediasMarkup().get())
    await state.clear()


@moderator_social_medias_router.message(F.text == SocialMediasMarkup.delete)
async def choose_sm_to_delete(message: Message):
    social_medias = await SocialMediaController.get_all_social_medias()
    markup = BaseInlineMarkup().get(buttons=[(sm.name, f"delete_sm:{sm.name}") for sm in social_medias])
    await message.answer("Choose a social media to delete:", reply_markup=markup)


@moderator_social_medias_router.callback_query(F.data.startswith("delete_sm"))
async def delete_sm(cb: CallbackQuery):
    _, name = cb.data.split(":")
    try:
        await SocialMediaController.delete_social_media(name)
    except Exception as e:
        await cb.bot.send_message(chat_id=cb.from_user.id, text=f"Error: {e}")
        return
    social_medias = await SocialMediaController.get_all_social_medias()
    markup = BaseInlineMarkup().get(buttons=[(sm.name, f"delete_sm:{sm.name}") for sm in social_medias])
    await cb.message.edit_reply_markup(reply_markup=markup)
    await cb.answer("Successfully deleted", show_alert=True)
