from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.consts import InlineConstructor
from states.girl.form import GirlFormStates


class GirlFormKeyboard(InlineConstructor):
    back_callback_data = CallbackData("GirlFormBack")
    @staticmethod
    def back():
        schema = [1]
        actions = [
            {'text': 'Назад', 'callback_data': ({}, GirlFormKeyboard.back_callback_data) }
        ]
        return GirlFormKeyboard._create_kb(actions, schema)


class GirlForm:

    def __init__(self):
        self.question_handlers = ["#1","#2", "#3"]

    def register_internal_handlers(self, dp: Dispatcher):
        # Во время опроса
        dp.register_message_handler(self.message_handler, state=GirlFormStates.entered)
        # Кнопка назад
        dp.register_callback_query_handler(
            self.back_query_handler,
            GirlFormKeyboard.back_callback_data.filter(),
            state=GirlFormStates.entered
        )

    async def back_query_handler(self, query: types.CallbackQuery, state: FSMContext):
        async with self.state.proxy() as data:
            data['question_number'] -= 2
            data['prev_question_message'] = None
            await query.message.delete()
        await self.send_question()

    async def message_handler(self, msg: types.Message, state: FSMContext):
        self.state = state
        self.msg = msg
        await self.send_question()

    async def send_question(self):
        async with self.state.proxy() as data:
            question_number = 0
            if qn := data.get('question_number'):
                question_number = qn
            else:
                await GirlFormStates.entered.set()

            if pqm := data.get("prev_question_message"):
                await pqm.edit_text(pqm.text)

            if question_number >= len(self.question_handlers):
                await self.state.finish()
                await self.msg.answer("Анкета заполнена ✅")
                return

            if question_number < 0:
                await self.state.finish()
                await self.msg.answer("Выхожу из анкеты ❌")
                return

            if question_number > 0 and not await self.process_answer():
                await self.msg.answer("Неверный формат, введите еще раз", reply_markup=GirlFormKeyboard.back())
                return
            question_message = await self.msg.answer( self.question_handlers[question_number], reply_markup=GirlFormKeyboard.back())

            data['prev_question_message'] = question_message
            data['question_number'] = question_number+1

    async def process_answer(self):
        return True