from aiogram import Dispatcher
from app.handlers.moderators_group.support import moderators_support_router
from app.handlers.moderators_group.feedback import moderators_feedback_router


def setup_moderators_group_handlers(dp: Dispatcher):
    dp.include_routers(
        moderators_support_router,
        moderators_feedback_router
    )
