from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from typing import List, Optional
from .. import async_session
from ..models.faq_message import FaqMessage


class FaqMessageController:
    @staticmethod
    async def get_faq_message(name: str) -> Optional[FaqMessage]:
        async with async_session() as session:
            try:
                faq_message = await session.scalar(
                    select(FaqMessage).where(FaqMessage.name == name)
                )
                return faq_message
            except NoResultFound:
                return None

    @staticmethod
    async def get_all_faq_messages() -> List[FaqMessage]:
        async with async_session() as session:
            faq_messages = (
                await session.scalars(
                    select(FaqMessage)
                )
            ).all()
            return faq_messages

    @staticmethod
    async def add_faq_message(
        name: str, message_id: int, chat_id: int
    ) -> FaqMessage:
        async with async_session() as session:
            message = FaqMessage(
                name=name, message_id=message_id, chat_id=chat_id
            )
            session.add(message)
            await session.commit()
            return message

    @staticmethod
    async def delete_faq_message(name: str) -> None:
        async with async_session() as session:
            try:
                faq_message = await session.scalar(
                    select(FaqMessage).where(FaqMessage.name == name)
                )
            except NoResultFound:
                return None
            await session.delete(faq_message)
            await session.commit()
