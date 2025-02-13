from sqlalchemy import select
from typing import List
from .. import async_session
from ..models.feedback import Feedback


class FeedbackController:
    @staticmethod
    async def get_feedback_by_id(feedback_id: int):
        async with async_session() as session:
            return await session.get(Feedback, feedback_id)

    @staticmethod
    async def delete_feedback_by_id(feedback_id: int):
        async with async_session() as session:
            feedback = await session.get(Feedback, feedback_id)
            if feedback:
                await session.delete(feedback)
                await session.commit()
                return True
            return False

    @staticmethod
    async def pin_feedback_by_id(feedback_id: int):
        async with async_session() as session:
            feedback = await session.get(Feedback, feedback_id)
            if feedback:
                feedback.is_pinned = True
                await session.commit()
                return True
            return False

    @staticmethod
    async def unpin_feedback_by_id(feedback_id: int):
        async with async_session() as session:
            feedback = await session.get(Feedback, feedback_id)
            if feedback:
                feedback.is_pinned = False
                await session.commit()
                return True
            return False

    @staticmethod
    async def create_feedback(chat_id: int, message_id: int, author_id: int, is_anonymous: bool = False,
                              approver_id: int = None):
        async with async_session() as session:
            new_feedback = Feedback(
                chat_id=chat_id,
                message_id=message_id,
                author_id=author_id,
                approver_id=approver_id,
                is_anonymous=is_anonymous
            )
            session.add(new_feedback)
            await session.commit()
            await session.refresh(new_feedback)
            return new_feedback

    @staticmethod
    async def get_all_feedbacks():
        result = await async_session().execute(
            select(Feedback).order_by(Feedback.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def get_pinned_feedbacks():
        result = await async_session().execute(
            select(Feedback).where(Feedback.is_pinned == True).order_by(Feedback.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def get_unpinned_feedbacks():
        result = await async_session().execute(
            select(Feedback).where(Feedback.is_pinned == False).order_by(Feedback.created_at)
        )
        return result.scalars().all()

    async def get_all_feedbacks_sorted(self):
        pinned = await self.get_pinned_feedbacks()
        unpinned = await self.get_unpinned_feedbacks()
        return pinned + unpinned

    async def get_feedbacks_page(self, page: int, per_page: int) -> List[Feedback]:
        all_feedbacks = await self.get_all_feedbacks_sorted()
        start = (page - 1) * per_page
        end = start + per_page
        return all_feedbacks[start:end]