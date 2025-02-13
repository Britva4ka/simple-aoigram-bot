from aiogram import Dispatcher
from app.middlewares.create_user_if_not_exists import CreateUserIfNotExistsMiddleware
from app.middlewares.user_is_banned import UserIsBannedMiddleware


def setup_middlewares(dp: Dispatcher):
    dp.update.middleware(CreateUserIfNotExistsMiddleware())
    dp.update.middleware(UserIsBannedMiddleware())
