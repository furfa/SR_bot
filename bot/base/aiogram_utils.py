from aiogram import types, Bot

from handlers.chat_history import CHAT_HISTORY


async def memorize_answer(msg: types.Message, *args, **kwargs):
    message = await msg.answer(*args, **kwargs)

    await CHAT_HISTORY.append(msg.chat.id, message)

    return message


async def memorize_send_message(bot: Bot, *args, **kwargs):
    message = await bot.send_message(*args, **kwargs)

    chat_id = kwargs.get("chat_id")
    if not chat_id:
        chat_id = args[0]

    await CHAT_HISTORY.append(chat_id, message)

    return message