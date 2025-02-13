from aiogram import Dispatcher
from app.handlers.admin.admin_menu import admin_menu_router


def setup_admin_handlers(dp: Dispatcher):
    dp.include_router(admin_menu_router)
