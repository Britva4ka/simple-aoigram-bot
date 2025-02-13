from . import Base
from sqlalchemy import Column, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship


class SupportSession(Base):
    __tablename__ = "support_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_thread_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)

    user = relationship("User", backref="support_sessions")
