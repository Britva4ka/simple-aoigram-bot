from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from database.models import Base
from config import DB_URL

engine = create_async_engine(DB_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
