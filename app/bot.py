from config import BOT_TOKEN, REDIS_URL
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage


if REDIS_URL:
    dp_storage = RedisStorage.from_url(REDIS_URL)
else:
    dp_storage = MemoryStorage()


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=dp_storage)
