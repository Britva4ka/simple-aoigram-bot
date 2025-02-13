from aiogram import Dispatcher
from app.handlers.private import setup_private_handlers
from app.handlers.moderator import setup_moderator_handlers
from app.handlers.moderators_group import setup_moderators_group_handlers
from app.handlers.admin import setup_admin_handlers


def setup_handlers(dp: Dispatcher):
    setup_private_handlers(dp)
    setup_moderator_handlers(dp)
    setup_moderators_group_handlers(dp)
    setup_admin_handlers(dp)
