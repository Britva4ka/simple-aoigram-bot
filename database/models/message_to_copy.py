from . import Base
from sqlalchemy import Column, Integer, BigInteger, String


class MessageToCopy(Base):
    __tablename__ = "messages_to_copy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    from_chat_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"MessageToCopy {self.key}"
