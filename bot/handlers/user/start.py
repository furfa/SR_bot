from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from loguru import logger

from base.aiogram_utils import memorize_answer
from base.cleaning import clean_message_decorator
from base.error_message import send_error_message
from keyboards.default import MainMenuKeyboard
from states.user.start import MainMenuStates
from templates.user.start import WELCOME_MESSAGE_NEW_USER, WELCOME_MESSAGE_MALE, WELCOME_MESSAGE_GIRL
from api.user import BackendUser


@clean_message_decorator
async def bot_start(msg: types.Message, state: FSMContext = None):
    bot = Bot.get_current()
    if state:
        await state.finish()

    user = None
    try:
        user = await BackendUser.create()
    except ValueError:
        pass

    if not user:
        user = await BackendUser.get()
    logger.info(f"{user=}")

    if user.sex == 'UNKNOWN':
        await memorize_answer(msg, WELCOME_MESSAGE_NEW_USER, reply_markup=MainMenuKeyboard.select_sex())
        await MainMenuStates.select_sex.set()
        return

    if user.sex == 'MALE':
        await bot.send_message(msg.chat.id, "Добро пожаловать в бота", reply_markup=MainMenuKeyboard.main_menu())
        await memorize_answer(msg, WELCOME_MESSAGE_MALE)
        return

    await msg.bot.send_message(msg.chat.id, "Добро пожаловать в бота", reply_markup=MainMenuKeyboard.main_menu())
    await memorize_answer(msg, WELCOME_MESSAGE_GIRL)


@clean_message_decorator
async def selected_sex(msg: types.Message, state: FSMContext = None):
    if msg.text == '👩🏽 Девушка':
        sex = "GIRL"
    elif msg.text == '👨🏽 Мужчина':
        sex = "MALE"
    else:
        await send_error_message("❗️ Нажмите кнопку на клавиатуре", msg=msg)
        return

    await state.finish()
    await BackendUser.update(sex=sex)
    await bot_start(msg, state)


async def delete_non_state_messages(msg: types.Message, state: FSMContext = None):
    await send_error_message("❗️ Выберите опцию на клавиатуре", msg=msg)