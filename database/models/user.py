from . import Base
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func
from config import ADMINS_ID


class User(Base):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    language_code = Column(String, nullable=False)
    is_moderator = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    has_banned_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def is_admin(self):
        return self.tg_id in ADMINS_ID
