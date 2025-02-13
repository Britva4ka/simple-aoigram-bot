import os
from dotenv import load_dotenv
import pytz

HOME_DIR = os.path.dirname(os.path.abspath(__file__))


load_dotenv()

timezone = pytz.timezone("Europe/Kyiv")

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODERATORS_SUPPORT_GROUP_ID = os.getenv("MODERATORS_SUPPORT_GROUP_ID")
MODERATORS_FEEDBACK_GROUP_ID = os.getenv("MODERATORS_FEEDBACK_GROUP_ID")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
POSTGRES_JOB_STORE = os.getenv("POSTGRES_JOB_STORE")

DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DATABASE}"
JOB_STORES_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_JOB_STORE}"
REDIS_URL = os.getenv("REDIS_URL")

WEB_APP_NAME = os.getenv("WEB_APP_NAME")
WEB_APP_URL = os.getenv("WEB_APP_URL")

SENTRY_DSN = os.getenv("SENTRY_DSN")

ADMINS_ID = os.getenv("ADMINS_ID", "").split(":") if os.getenv("ADMINS_ID") else []
