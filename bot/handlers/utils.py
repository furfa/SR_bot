import asyncio

from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from loguru import logger

from handlers.chat_history import CHAT_HISTORY


def get_clear_history_answer(msg):
    async def answer(*args, **kwargs):
        user = types.User.get_current()
        bot = Bot.get_current()
        for message in await CHAT_HISTORY.get(user_id=user.id):
            try:
                await bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                logger.error( f"error while deleting {message=}" )

        message = await types.Message.answer(msg, *args, **kwargs)
        await CHAT_HISTORY.set(user_id=user.id, message_order=[message])

        return message
    return answer


def clean_message_decorator(func):
    async def inner(msg: types.Message, state: FSMContext):
        await msg.delete()
        msg.answer = get_clear_history_answer(msg)
        return await func(msg, state)

    return inner


def get_history_logger_answer(msg):
    async def answer(*args, **kwargs):
        message = await types.Message.answer(msg, *args, **kwargs)
        await CHAT_HISTORY.append(types.User.get_current().id, message)
        return message
    return answer


async def send_error_message(text, msg=None):
    if msg is None:
        user = types.User.get_current()
        bot = Bot.get_current()
        message = await bot.send_message(user.id, text)
    else:
        message = await msg.reply(text)

    await asyncio.sleep(0.5)
    await message.delete()

    if msg:
        await msg.delete()
