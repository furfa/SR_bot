from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.utils import clean_message_decorator
from utils.misc import rate_limit


@clean_message_decorator
async def bot_help(msg: types.Message, state: FSMContext):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку'
    ]
    await msg.answer('\n'.join(text))
