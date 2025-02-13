from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import ForumTopic, Message, CallbackQuery
from aiogram import Bot
import asyncio
import logging


async def copy_message_with_retry(bot: Bot, user_id, from_user_id, message_id, reply_markup=None):
    try:
        return await bot.copy_message(user_id, from_user_id, message_id, reply_markup=reply_markup)
    except TelegramRetryAfter as e:
        logging.warning(
            f"Rate limit exceeded. Retrying in {e.retry_after + 1} seconds..."
        )
        await asyncio.sleep(e.retry_after + 1)
        return await copy_message_with_retry(bot, user_id, from_user_id, message_id, reply_markup)
    except Exception as e:
        logging.error(e)
        raise e


async def create_forum_topic_with_retry(bot, chat_id, name, message: Message | CallbackQuery = None) -> ForumTopic:
    try:
        topic = await bot.create_forum_topic(chat_id=chat_id, name=name)
        return topic
    except TelegramRetryAfter as e:
        logging.warning(
            f"Rate limit exceeded. Retrying in {e.retry_after+1} seconds..."
        )
        if message:
            await message.bot.send_message(
                chat_id=message.from_user.id,
                text="Rate limit exceeded. Retrying in {e.retry_after+1} seconds..."
            )
        await asyncio.sleep(e.retry_after + 1)
        return await create_forum_topic_with_retry(bot, chat_id, name)


async def delete_forum_topic_with_retry(bot, chat_id, message_thread_id):
    try:
        await bot.delete_forum_topic(chat_id=chat_id, message_thread_id=message_thread_id)
    except TelegramRetryAfter as e:
        logging.warning(
            f"Rate limit exceeded. Retrying in {e.retry_after+1} seconds..."
        )
        await asyncio.sleep(e.retry_after + 1)
        return await delete_forum_topic_with_retry(bot, chat_id, message_thread_id)
    except Exception as e:
        logging.warning(e)
