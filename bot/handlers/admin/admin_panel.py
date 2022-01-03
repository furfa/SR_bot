from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from loguru import logger
from contextlib import suppress

from api.user import BackendUser, UserSupportQuestion
from keyboards.default.admin_panel import AdminMenuKeyboard
from keyboards.inline.admin_panel import AdminQuestionInline
from states.admin.admin_panel import AdminPanelStates
from templates.admin.admin_panel import SUPPORT_QUESTION_TEMPLATE, NO_SUPPORT_QUESTIONS
from templates.user.support import QUESTION_ANSWERED


async def admin_enter(msg: types.Message):
    if not await BackendUser.check_is_admin(): # TODO: Вынести в декоротор
        return

    await AdminPanelStates.menu.set()
    await msg.answer("Добро пожаловать в админку", reply_markup=AdminMenuKeyboard.admin_menu())


async def support_admin(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return

    await AdminPanelStates.support_admin.set()
    await msg.answer("Выберите на какой тип поддержки вы хотите отвечать",
                     reply_markup=AdminMenuKeyboard.support_menu())


def get_filtered_support_messages_handler(filter_word):
    async def inner(msg: types.Message, state: FSMContext = None):
        questions = await UserSupportQuestion.list(type_filter=filter_word)

        if not questions:
            await msg.answer(
                NO_SUPPORT_QUESTIONS
            )
            return

        for question in questions:
            await msg.answer(
                SUPPORT_QUESTION_TEMPLATE.format(question=question.question_body, user=question.user),
                reply_markup=AdminQuestionInline.answer(question.id)
            )

    return inner


async def answer_question(query: types.CallbackQuery, callback_data: dict):
    from app import bot
    text = query.message.text
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(query.from_user.id, text=text+"\n"+("="*10)+"\n Напишите ответ 👇", )
    await AdminPanelStates.support_answer.set()

    state = Dispatcher.get_current().current_state()
    async with state.proxy() as data:
        data['id'] = callback_data["id"]


async def answer_handler(msg: types.Message, state: FSMContext = None):
    async with state.proxy() as data:
        changed = await UserSupportQuestion.update(id_=data['id'], answer_body=msg.text)

        bot = Bot.get_current()
        await bot.send_message(
            changed.user,
            QUESTION_ANSWERED.format(question=changed.question_body, answer=changed.answer_body)
        )

    await msg.answer("Записано👌")
    await AdminPanelStates.support_admin.set()