from . import Base
from sqlalchemy import Column, Integer, String, DateTime, func


class FaqMessage(Base):
    __tablename__ = 'faq_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    message_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<FaqMessage {self.name}>"
