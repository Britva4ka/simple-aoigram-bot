from aiogram import Dispatcher
from app.handlers.private.start_menu import start_menu_router
from app.handlers.private.social_media import social_media_router
from app.handlers.private.support import support_router
from app.handlers.private.feedback import feedback_router
from app.handlers.private.faq import faq_message_router


def setup_private_handlers(dp: Dispatcher):
    dp.include_routers(
        start_menu_router,
        social_media_router,
        support_router,
        feedback_router,
        faq_message_router
    )
