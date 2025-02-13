from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from typing import Optional
from .. import async_session
from ..models.message_to_copy import MessageToCopy


class MessageToCopyController:
    @staticmethod
    async def get_message(key: str) -> Optional[MessageToCopy]:
        async with async_session() as session:
            try:
                message = await session.scalar(
                    select(MessageToCopy).where(MessageToCopy.key == key)
                )
                return message
            except NoResultFound:
                return None

    @staticmethod
    async def add_message(
        key: str, message_id: int, from_chat_id: int
    ) -> MessageToCopy:
        async with async_session() as session:
            message = MessageToCopy(
                key=key, message_id=message_id, from_chat_id=from_chat_id
            )
            session.add(message)
            await session.commit()
            return message

    @staticmethod
    async def update_message(
        key: str, new_message_id: int, new_from_chat_id: int
    ) -> bool:
        async with async_session() as session:
            message = await session.scalar(
                select(MessageToCopy).where(MessageToCopy.key == key)
            )
            if message:
                message.message_id = new_message_id
                message.from_chat_id = new_from_chat_id
                await session.commit()
                return True
            return False