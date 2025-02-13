from . import Base
from sqlalchemy import Column, Integer, String, DateTime, func


class SocialMedia(Base):
    __tablename__ = 'social_medias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<SocialMedia {self.name}>"
