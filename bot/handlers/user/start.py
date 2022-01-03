from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger
from contextlib import suppress

from keyboards.default import MainMenuKeyboard
from states.user.start import MainMenuStates
from templates.user.start import WELCOME_MESSAGE_NEW_USER, WELCOME_MESSAGE_MALE, WELCOME_MESSAGE_GIRL
from api.user import BackendUser


async def bot_start(msg: types.Message, state: FSMContext = None):
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
        await msg.answer(WELCOME_MESSAGE_NEW_USER, reply_markup=MainMenuKeyboard.select_sex())
        await MainMenuStates.select_sex.set()
        return

    if user.sex == 'MALE':
        await msg.answer(WELCOME_MESSAGE_MALE, reply_markup=MainMenuKeyboard.main_menu())
        return

    await msg.answer(WELCOME_MESSAGE_GIRL, reply_markup=MainMenuKeyboard.main_menu())


async def selected_male(msg: types.Message, state: FSMContext = None):
    await BackendUser.update(sex="MALE")
    await state.finish()
    await bot_start(msg)


async def selected_girl(msg: types.Message, state: FSMContext = None):
    await BackendUser.update(sex="GIRL")
    await state.finish()
    await bot_start(msg)