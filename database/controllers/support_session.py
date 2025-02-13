from sqlalchemy import select, func
from .. import async_session
from ..models.support_session import SupportSession


class SupportSessionController:

    @staticmethod
    async def get_session_by_id(session_id: int):
        async with async_session() as session:
            return await session.get(SupportSession, int(session_id))

    @staticmethod
    async def create_session(message_thread_id: int, user_id: int):
        async with async_session() as session:
            new_session = SupportSession(
                message_thread_id=int(message_thread_id),
                user_id=int(user_id)
            )
            session.add(new_session)
            await session.commit()
            await session.refresh(new_session)
            return new_session

    @staticmethod
    async def delete_session(session_id: int):
        async with async_session() as session:
            support_session = await session.get(SupportSession, int(session_id))
            if support_session:
                await session.delete(support_session)
                await session.commit()
                return True
            return False

    @staticmethod
    async def get_sessions_amount():
        async with async_session() as session:
            result = await session.execute(
                select(func.count()).select_from(SupportSession)
            )
            return result.scalar()