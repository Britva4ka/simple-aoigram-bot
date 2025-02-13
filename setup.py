import logging
from app.bot import bot, dp
from app.scheduler import setup_scheduler
from logs import setup_logging
from app.handlers import setup_handlers
from app.middlewares import setup_middlewares
from aiogram.types import BotCommand, BotCommandScopeChat, MenuButtonWebApp, WebAppInfo
from config import MODERATORS_SUPPORT_GROUP_ID, MODERATORS_FEEDBACK_GROUP_ID, WEB_APP_URL, WEB_APP_NAME, SENTRY_DSN
import sentry_sdk


async def on_startup():
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text=WEB_APP_NAME, web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    await bot.set_my_commands(
        [
            BotCommand(command="help", description="Support Manual"),
        ],
        scope=BotCommandScopeChat(chat_id=MODERATORS_SUPPORT_GROUP_ID)
    )
    await bot.set_my_commands(
        [
            BotCommand(command="help", description="Feedback Manual"),
        ],
        scope=BotCommandScopeChat(chat_id=MODERATORS_FEEDBACK_GROUP_ID)
    )


async def on_shutdown():
    logging.warning("Good bye")


async def main() -> None:
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            send_default_pii=True,
            traces_sample_rate=1.0,
            _experiments={
                "continuous_profiling_auto_start": True,
            },
        )
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    setup_logging()
    setup_middlewares(dp)
    setup_handlers(dp)
    await setup_scheduler()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
