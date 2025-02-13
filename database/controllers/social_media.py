from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from typing import List, Optional
from .. import async_session
from ..models.social_media import SocialMedia


class SocialMediaController:
    @staticmethod
    async def get_social_media(name: str) -> Optional[SocialMedia]:
        async with async_session() as session:
            try:
                social_media = await session.scalar(
                    select(SocialMedia).where(SocialMedia.name == name)
                )
                return social_media
            except NoResultFound:
                return None

    @staticmethod
    async def get_all_social_medias() -> List[SocialMedia]:
        async with async_session() as session:
            social_medias = (
                await session.scalars(
                    select(SocialMedia)
                )
            ).all()
            return social_medias

    @staticmethod
    async def add_social_media(
        name: str, url: str
    ) -> SocialMedia:
        async with async_session() as session:
            message = SocialMedia(
                name=name, url=url
            )
            session.add(message)
            await session.commit()
            return message

    @staticmethod
    async def delete_social_media(name: str) -> None:
        async with async_session() as session:
            try:
                social_media = await session.scalar(
                    select(SocialMedia).where(SocialMedia.name == name)
                )
            except NoResultFound:
                return None
            await session.delete(social_media)
            await session.commit()