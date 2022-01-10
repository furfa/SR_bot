from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from . import form


async def setup(dp: Dispatcher):
    girl_form = await form.GirlForm.create()
    dp.register_message_handler(girl_form.message_handler, text=["/girl_register_form"])
    girl_form.register_internal_handlers(dp)
