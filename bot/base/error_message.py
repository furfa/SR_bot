import asyncio

from aiogram import types, Bot


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