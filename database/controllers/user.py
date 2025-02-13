from sqlalchemy import select, func, desc, update
from sqlalchemy.exc import NoResultFound
from typing import List, Optional
from .. import async_session
from ..models.user import User


class UserController:
    @staticmethod
    async def get_all_users() -> List[User]:
        async with async_session() as session:
            users = (
                await session.scalars(
                    select(User)
                )
            ).all()
            return users

    @staticmethod
    async def get_all_moderators() -> List[User]:
        async with async_session() as session:
            moderators = (
                await session.scalars(
                    select(User)
                    .where(User.is_moderator == True)
                )
            ).all()
            return moderators

    @staticmethod
    async def create_new_user(
            tg_id: int,
            username: str,
            full_name: str,
            language_code: str,
            is_moderator: bool = False,
    ) -> User:
        async with async_session() as session:
            user = User(
                tg_id=tg_id,
                username=username,
                full_name=full_name,
                language_code=language_code,
                is_moderator=is_moderator,
            )
            session.add(user)
            await session.commit()
            return user

    @staticmethod
    async def get_user_by_id(tg_id: int) -> Optional[User]:
        async with async_session() as session:
            try:
                user = await session.scalar(
                    select(User)
                    .where(User.tg_id == tg_id)
                )
                return user
            except NoResultFound:
                return None

    @staticmethod
    async def switch_user_moderator(tg_id: int) -> bool:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.is_moderator = not user.is_moderator
                session.add(user)
                await session.commit()
                return True
            return False

    @staticmethod
    async def switch_user_ban(tg_id: int) -> bool:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.is_banned = not user.is_banned
                session.add(user)
                await session.commit()
                return True
            return False

    @staticmethod
    async def get_moderators_by_page(page: int, page_size: int = 20):
        offset = (page - 1) * page_size
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .filter(User.is_moderator == True)
                .order_by(desc(User.created_at))
                .offset(offset)
                .limit(page_size)
            )
            moderators = result.scalars().all()
        return moderators

    @staticmethod
    async def get_banned_users_by_page(page: int, page_size: int = 20):
        offset = (page - 1) * page_size
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .filter(User.is_banned == True)
                .order_by(desc(User.created_at))
                .offset(offset)
                .limit(page_size)
            )
            banned_users = result.scalars().all()
        return banned_users

    @staticmethod
    async def set_has_banned_bot(tg_id: int, banned: bool) -> None:
        async with async_session() as session:
            await session.execute(
                update(User)
                .where(User.tg_id == tg_id)
                .values(has_banned_bot=banned)
            )
            await session.commit()

    @staticmethod
    async def mark_bot_as_banned(tg_id: int) -> None:
        await UserController.set_has_banned_bot(tg_id, True)

    @staticmethod
    async def mark_bot_as_unbanned(tg_id: int) -> None:
        await UserController.set_has_banned_bot(tg_id, False)