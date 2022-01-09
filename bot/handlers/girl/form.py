import aiogram
from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram import exceptions
from aiogram.utils.callback_data import CallbackData
from loguru import logger

from keyboards.inline.consts import InlineConstructor
from states.girl.form import GirlFormStates


class GirlFormKeyboard(InlineConstructor):
    back_callback_data = CallbackData("GirlFormBack")
    button_choices_callback_data = CallbackData("ButtonChoices", "question_num", "option_num")
    checkbox_choices_callback_data = CallbackData("CheckBoxChoices", "question_num", "option_num")

    @staticmethod
    def back():
        schema = [1]
        actions = [
            {'text': 'Назад', 'callback_data': ({}, GirlFormKeyboard.back_callback_data)}
        ]
        return GirlFormKeyboard._create_kb(actions, schema)

    @staticmethod
    def button_choices(choices, question_num):
        actions = [
            *[{'text': choice, 'callback_data': (
                {
                    'question_num': question_num,
                    'option_num': index
                },
                GirlFormKeyboard.button_choices_callback_data
            )}
              for index, choice in enumerate(choices)],
            {'text': 'Назад', 'callback_data': ({}, GirlFormKeyboard.back_callback_data)}
        ]
        schema = [1] * len(actions)
        return GirlFormKeyboard._create_kb(actions, schema)

    @staticmethod
    def checkbox_choices(choices, selected_choices, question_num):
        actions = [
            *[{'text': choice + " " + ("✅" if index in selected_choices else "❌"), 'callback_data': (
                {
                    'question_num': question_num,
                    'option_num': index
                },
                GirlFormKeyboard.checkbox_choices_callback_data
            )}
              for index, choice in enumerate(choices)],
            {'text': 'Сохранить ✏️', 'callback_data': (
            {'question_num': question_num, 'option_num': "save"}, GirlFormKeyboard.checkbox_choices_callback_data)},
            {'text': 'Назад', 'callback_data': ({}, GirlFormKeyboard.back_callback_data)}
        ]
        schema = [1] * len(actions)
        return GirlFormKeyboard._create_kb(actions, schema)


QUESTIONS = (
    {
        "type": "text_input",
        "text": "Какой у тебя рост?",
        "validators": lambda x: x.isdigit(),
        "processor": lambda x: None
    },
    {
        "type": "button_choices",
        "choices": [
            "Новосибирск",
            "Москва"
        ],
        "text": "Выбери свой город",
        "validators": lambda x: True,
        "processor": lambda x: None
    },
    {
        "type": "multicheckbox",
        "choices": ["Паспорт", "Виза"],
        "text": "Выбери имеющиеся документы",
        "validators": lambda x: True,
        "processor": lambda x: None
    },
    {
        "type": "yes_no",
        "text": "Скажите да или нет",
        "validators": lambda x: True,
        "processor": lambda x: None
    }
)


class GirlForm:

    def __init__(self):
        self.question_handlers = QUESTIONS

    def register_internal_handlers(self, dp: Dispatcher):
        # Во время опроса
        dp.register_message_handler(self.message_handler, state=GirlFormStates.entered)
        # Кнопка назад
        dp.register_callback_query_handler(
            self.back_query_handler,
            GirlFormKeyboard.back_callback_data.filter(),
            state=GirlFormStates.entered
        )
        # Callbacks от кнопок с выбором
        dp.register_callback_query_handler(
            self.button_choices_query_handler,
            GirlFormKeyboard.button_choices_callback_data.filter(),
            state=GirlFormStates.entered
        )
        # Callbacks от кнопок с чекбоксом
        dp.register_callback_query_handler(
            self.checkbox_choices_query_handler,
            GirlFormKeyboard.checkbox_choices_callback_data.filter(),
            state=GirlFormStates.entered
        )

    async def button_choices_query_handler(self, query: types.CallbackQuery, state: FSMContext, callback_data: dict):
        question_num = int(callback_data["question_num"])
        option_num = int(callback_data["option_num"])
        if self.question_handlers[question_num]["type"] == "button_choices":
            choices = self.question_handlers[question_num]["choices"]
        elif self.question_handlers[question_num]["type"] == "yes_no":
            choices = [True, False]
        else:
            logger.error("not allowed action")
            return
        choice = choices[option_num]

        if question_num >= 0 and not await self.validate_answer(choice, question_num):
            await query.message.answer("Неверный формат, введите еще раз", reply_markup=GirlFormKeyboard.back())
            return

        await query.message.edit_text(query.message.text)
        if self.question_handlers[question_num]["type"] == "yes_no":
            await query.message.answer(f"👉 {'Да' if choice else 'Нет'}")
        else:
            await query.message.answer(f"👉 {choice}")
        await self.send_question(query.message, state)

    async def checkbox_choices_query_handler(self, query: types.CallbackQuery, state: FSMContext, callback_data: dict):
        async with state.proxy() as data:
            question_num = int(callback_data["question_num"])

            if self.question_handlers[question_num]["type"] != "multicheckbox":
                logger.error("not allowed action")
                return
            data["selected_choices"] = data.get("selected_choices", {})
            data["selected_choices"][question_num] = data["selected_choices"].get(question_num, [])

            if callback_data["option_num"] == "save":
                question_text = self.question_handlers[question_num]["text"]
                res_str = "\n".join(
                    "🔹 " + self.question_handlers[question_num]["choices"][choice_index] for choice_index in
                    data["selected_choices"][question_num])
                await query.message.delete()
                await query.message.answer(question_text + "\n\n<b>Выбрано:</b> \n" + res_str)
                await self.send_question(query.message, state)
                return

            option_num = int(callback_data["option_num"])

            if option_num in data["selected_choices"][question_num]:
                data["selected_choices"][question_num].remove(option_num)
            else:
                data["selected_choices"][question_num].append(option_num)

            await query.message.edit_text(
                query.message.text,
                reply_markup=GirlFormKeyboard.checkbox_choices(
                    self.question_handlers[question_num]["choices"],
                    data["selected_choices"][question_num],
                    question_num
                )
            )

    async def back_query_handler(self, query: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['question_number'] = data.get('question_number', 0)
            data['question_number'] -= 2
            await query.message.delete()
            question_number = data['question_number']
        logger.error(f"{question_number=}")
        if question_number < -1:
            await state.finish()
            await query.message.answer("Выхожу из анкеты ❌")
            return

        await self.send_question(query.message, state)

    async def message_handler(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            logger.info(f"{dict(data)= } {msg=}")
            question_number = data.get('question_number', -100)

            if (
                    question_number >= 0 and
                    self.question_handlers[question_number]["type"] != "text_input"
            ):
                await msg.answer("⛔ Неверный формат, введите еще раз")
                return

            if (
                    question_number >= 0 and
                    not await self.validate_answer(msg.text, question_number)
            ):
                if pqm := data.get("prev_question_message"):
                    await pqm.edit_text("<b>⛔️ Неверный формат, введите еще раз</b>\n" + pqm.text,
                                        reply_markup=GirlFormKeyboard.back())
                    await msg.delete()
                else:
                    await msg.answer("⛔️ Неверный формат, введите еще раз", reply_markup=GirlFormKeyboard.back())
                return

        await self.send_question(msg, state)

    async def send_question(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if not data.get('question_number') is None:
                data['question_number'] += 1
            else:
                data['question_number'] = 0
                await GirlFormStates.entered.set()
            question_number = data['question_number']
            try:
                if pqm := data.get("prev_question_message"):
                    await pqm.edit_text(pqm.text)  # delete inline buttons
            except (exceptions.MessageNotModified, exceptions.MessageToEditNotFound) as e:
                logger.error("error while deleting markup")

        if question_number >= len(self.question_handlers):
            await state.finish()
            await msg.answer("Анкета заполнена ✅")
            return

        async with state.proxy() as data:
            data['prev_question_message'] = await self.send_question_message(msg, state, question_number)

    async def send_question_message(self, msg: types.Message, state: FSMContext, question_number: int):
        async with state.proxy() as data:
            handler = self.question_handlers[question_number]
            print(handler)

            if handler["type"] == "text_input":
                return await msg.answer(handler["text"], reply_markup=GirlFormKeyboard.back())

            if handler["type"] == "button_choices":
                return await msg.answer(handler["text"],
                                        reply_markup=GirlFormKeyboard.button_choices(handler["choices"],
                                                                                     question_number))

            if handler["type"] == "multicheckbox":
                return await msg.answer(handler["text"],
                                        reply_markup=GirlFormKeyboard.checkbox_choices(
                                            handler["choices"],
                                            data.get("selected_choices", {}).get(question_number, []),
                                            question_number))

            if handler["type"] == "yes_no":
                return await msg.answer(handler["text"],
                                        reply_markup=GirlFormKeyboard.button_choices(
                                            ["✅ Да", "❌ Нет"],
                                            question_number
                                        ))

    async def validate_answer(self, text: str, question_number: int):
        handler = self.question_handlers[question_number]
        return handler["validators"](text)

    async def process_answer(self, msg: types.Message, state: FSMContext, question_number: int):
        handler = self.question_handlers[question_number]
        handler["processor"](msg)
