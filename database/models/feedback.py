from . import Base
from sqlalchemy import Column, Integer, BigInteger, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    author_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    approver_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=True)

    author = relationship("User", foreign_keys=[author_id])
    approver = relationship("User", foreign_keys=[approver_id])

    def __repr__(self):
        return f"<Feedback {self.id} from {self.author.username}>"
