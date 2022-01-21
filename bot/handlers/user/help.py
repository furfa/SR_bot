from aiogram import types
from aiogram.dispatcher import FSMContext

from base.aiogram_utils import memorize_answer
from base.cleaning import clean_message_decorator


@clean_message_decorator
async def bot_help(msg: types.Message, state: FSMContext):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку'
    ]
    await memorize_answer(msg, '\n'.join(text))
