import asyncio

from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from loguru import logger

from handlers.chat_history import CHAT_HISTORY


async def clean_history():
    user = types.User.get_current()
    bot = Bot.get_current()
    for message in await CHAT_HISTORY.get(user_id=user.id):
        try:
            await bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            logger.error(f"error while deleting {message=}")

    await CHAT_HISTORY.set(user_id=user.id, message_order=[])


def clean_message_decorator(func):
    async def inner(msg: types.Message, state: FSMContext):
        await msg.delete()
        await clean_history()
        return await func(msg, state)

    return inner


def get_history_logger_answer(msg):
    async def answer(*args, **kwargs):
        message = await types.Message.answer(msg, *args, **kwargs)
        await CHAT_HISTORY.append(types.User.get_current().id, message)
        return message
    return answer
