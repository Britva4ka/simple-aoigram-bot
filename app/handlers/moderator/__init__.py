from aiogram import Dispatcher
from app.handlers.moderator.moderator_menu import moderator_menu_router
from app.handlers.moderator.broadcasting import moderator_broadcast_router
from app.handlers.moderator.messages import moderator_messages_router
from app.handlers.moderator.social_media import moderator_social_medias_router
from app.handlers.moderator.faq import moderator_faq_router


def setup_moderator_handlers(dp: Dispatcher):
    dp.include_routers(
        moderator_menu_router,
        moderator_broadcast_router,
        moderator_messages_router,
        moderator_social_medias_router,
        moderator_faq_router
    )
