from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from loguru import logger
from contextlib import suppress

from api.user import UserSupportQuestion
from handlers.chat_history import CHAT_HISTORY
from handlers.utils import clean_message_decorator, get_history_logger_answer
from keyboards.default import MainMenuKeyboard
from keyboards.inline.support import SupportKeyboardInline
from templates.user import support as templates
from states.user.support import SupportStates


@clean_message_decorator
async def support_start(msg: types.Message, state: FSMContext):
    await msg.answer(text=templates.SUPPORT_START, reply_markup=SupportKeyboardInline.menu())


async def back_to_support(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.finish()
    await query.message.edit_text(templates.SUPPORT_START, reply_markup=SupportKeyboardInline.menu())


async def partnership_support_info(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await query.message.edit_text(templates.PARTNERSHIP_SUPPORT_MESSAGE, reply_markup=SupportKeyboardInline.partner_support_menu())


async def faq_info(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await query.message.delete() # Костыль, чтобы на айфоне кнопки не блокировались. В идеале делать edit text.

    query.message.answer = get_history_logger_answer(query.message)
    await query.message.answer(templates.FAQ_MESSAGE, reply_markup=SupportKeyboardInline.faq_menu())


async def faq_display_question_answer(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    qn = callback_data.get("question_num")
    if not qn:
        return
    text = templates.FAQ_CONTENT[int(qn)]["answer"]

    await query.message.edit_text(
        text,
        reply_markup=SupportKeyboardInline.back_to_faq_menu()
    )


async def support_callback_handler(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    support_type = callback_data.get("type")
    if not support_type:
        return

    msg: types.Message = query.message

    await msg.delete()

    text = "None"
    if support_type == "tech_support":
        await SupportStates.technical.set()
        text = templates.TECHNICAL_SUPPORT_QUESTION
    if support_type == "partner_support":
        await SupportStates.partnership.set()
        text = templates.PARTNERSHIP_SUPPORT_QUESTION
    if support_type == "client_support":
        await SupportStates.client.set()
        text = templates.CLIENT_SUPPORT_QUESTION

    msg.answer = get_history_logger_answer(msg)

    question_message = await msg.answer(
        text,
        reply_markup=SupportKeyboardInline.back_to_support_menu()
    )
    async with state.proxy() as data:
        data['question_message'] = question_message


async def question_handler(msg: types.Message, state: FSMContext = None):
    type = "CLIENT"
    state_str = await state.get_state()
    print(state_str)
    if state_str == "SupportStates:partnership":
        type = "PARTNERSHIP"

    if state_str == "SupportStates:client":
        type = "CLIENT"

    if state_str == "SupportStates:technical":
        type = "TECHNICAL"

    await UserSupportQuestion.create(msg.text, type)

    # Delete message
    await msg.delete()

    # Delete question message
    async with state.proxy() as data:
        if m := data.get('question_message'):
            await m.delete()

    # Finish state
    if state:
        await state.finish()

    msg.answer = get_history_logger_answer(msg)
    await msg.answer(templates.THANKS_FOR_ANSWER.format(question=msg.text))