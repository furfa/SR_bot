from __future__ import annotations

import aiogram
from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from loguru import logger

import api.girl_form
from handlers.girl.base_questions import QuestionTree

from handlers.girl.secret_room import display_girl_form
from keyboards.inline.consts import InlineConstructor


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
        len_actions = len(actions) - 1
        schema = [3] * (len_actions // 3) + [len_actions % 3] + [1]
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


class GirlFormBase:

    def __init__(self, enter_state, need_approve):
        self.enter_state = enter_state
        self.need_approve = need_approve
        self.question_handlers = QuestionTree.from_nodes()

    def register_internal_handlers(self, dp: Dispatcher):
        # Во время опроса
        dp.register_message_handler(self.message_handler, state=self.enter_state)
        dp.register_message_handler(self.media_handler, state=self.enter_state, content_types=["photo", "video"])
        # Кнопка назад
        dp.register_callback_query_handler(
            self.back_query_handler,
            GirlFormKeyboard.back_callback_data.filter(),
            state=self.enter_state
        )
        # Callbacks от кнопок с выбором
        dp.register_callback_query_handler(
            self.button_choices_query_handler,
            GirlFormKeyboard.button_choices_callback_data.filter(),
            state=self.enter_state
        )
        # Callbacks от кнопок с чекбоксом
        dp.register_callback_query_handler(
            self.checkbox_choices_query_handler,
            GirlFormKeyboard.checkbox_choices_callback_data.filter(),
            state=self.enter_state
        )

    async def button_choices_query_handler(self, query: types.CallbackQuery, state: FSMContext, callback_data: dict):
        question_num = callback_data["question_num"]
        option_num = int(callback_data["option_num"])

        question_obj = self.question_handlers.get(question_num)
        if question_obj.type == "button_choices":
            choices = await question_obj.choices()
        else:
            logger.error("not allowed action")
            return
        choice = choices[option_num]

        if not (await question_obj.validator(choice)):
            await query.message.answer("Неверный формат, введите еще раз", reply_markup=GirlFormKeyboard.back())
            return

        await query.message.edit_text(query.message.text)
        await question_obj.processor(msg=None, choice=choice)
        await self.send_question(query.message, state)

    async def checkbox_choices_query_handler(self, query: types.CallbackQuery, state: FSMContext, callback_data: dict):
        async with state.proxy() as data:
            question_num = callback_data["question_num"]

            if self.question_handlers.get(question_num).type != "multicheckbox":
                logger.error("not allowed action")
                return
            data["selected_choices"] = data.get("selected_choices", {})
            data["selected_choices"][question_num] = data["selected_choices"].get(question_num, [])

            if callback_data["option_num"] == "save":
                question_obj = self.question_handlers.get(question_num)
                question_text = question_obj.text
                choices = await question_obj.choices()
                selected_choices = [choices[choice_index] for choice_index in
                                    data["selected_choices"][question_num]]
                res_str = "\n".join(
                    "🔹 " + choice for choice in selected_choices)
                await query.message.delete()
                await question_obj.processor(choice=selected_choices, msg=None)
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
                    await self.question_handlers.get(question_num).choices(),
                    data["selected_choices"][question_num],
                    question_num
                )
            )

    async def back_query_handler(self, query: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['question_number'] = data.get('question_number', self.question_handlers.get_start())
            data['question_number'] = await self.question_handlers.get(data['question_number']).prev()
            if data['question_number'] != "ENTER":
                data['question_number'] = await self.question_handlers.get(data['question_number']).prev()
            await query.message.delete()
            question_number = data['question_number']
        logger.error(f"{question_number=}")
        if question_number == "ENTER":
            if form_info_message := (await state.get_data()).get("form_info_message"):
                await form_info_message.delete()
            await state.finish()
            await query.message.answer("Выхожу из анкеты ❌", disable_notification=True)
            return

        await self.send_question(query.message, state)

    async def enter_inline(self, query: types.CallbackQuery, state: FSMContext):
        await query.message.delete()
        # try:
        #     await api.girl_form.GirlForm.get()
        # except ValueError:
        if self.need_approve:
            await api.girl_form.GirlForm.create()
        await self.message_handler(query.message, state)

    async def media_handler(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            question_number = data.get('question_number')
        await msg.delete()
        warning = "⛔️ Неверный формат, введите еще раз"
        if not msg.photo or (question_number and self.question_handlers.get(question_number).type != "media"):
            if pqm := data.get("prev_question_message"):
                # resend message
                await pqm.delete()
                new_text = ("" if warning in pqm.text else "<b>" + warning + "</b>\n") + pqm.text
                data["prev_question_message"] = await pqm.answer(
                    new_text,
                    reply_markup=pqm.reply_markup
                )
            else:
                await msg.answer("<b>" + warning + "</b>", reply_markup=GirlFormKeyboard.back())
            return

        print(f"{msg=} {question_number=}")
        await self.question_handlers.get(question_number).processor(msg, choice=None)
        await self.send_question(msg, state)

    async def message_handler(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            logger.info(f"{dict(data)= } {msg=}")
            question_number = data.get('question_number')
            print(f"{question_number=}")
            if msg.chat.id == msg.from_user.id:
                await msg.delete()

            warning = "⛔️ Неверный формат, введите еще раз"
            question_obj = self.question_handlers.get(question_number)

            if (
                    question_obj and (
                    question_obj.type != "text_input" or
                    not await question_obj.validator(msg.text)
            )
            ):
                if pqm := data.get("prev_question_message"):
                    # resend message
                    await pqm.delete()
                    new_text = ("" if warning in pqm.text else "<b>" + warning + "</b>\n") + pqm.text
                    data["prev_question_message"] = await pqm.answer(
                        new_text,
                        reply_markup=pqm.reply_markup
                    )
                else:
                    data["prev_question_message"] = await msg.answer("<b>" + warning + "</b>",
                                                                     reply_markup=GirlFormKeyboard.back())
                return
        if question_obj:
            await question_obj.processor(msg, choice=None)
        await self.send_question(msg, state)

    async def send_question(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if not data.get('question_number') is None:
                question_number = data['question_number']
                qn = await self.question_handlers.get(question_number).next()
                data['question_number'] = qn
            else:
                data['question_number'] = self.question_handlers.get_start()
                await self.enter_state.set()

            question_number = data['question_number']
            logger.info(f"send_question {question_number=}")
            try:
                if pqm := data.get("prev_question_message"):
                    await pqm.delete()
            except Exception as e:
                logger.error("error while deleting markup")

        async with state.proxy() as data:
            if question_number == "EXIT":
                await state.finish()
                await msg.answer("Анкета заполнена ✅", disable_notification=True)
                form_info_message = data.get("form_info_message")
                if form_info_message:
                    await form_info_message.delete()
                if self.need_approve:
                    await api.girl_form.GirlForm.set_filled()
                return

        async with state.proxy() as data:
            info_text = await display_girl_form(await api.girl_form.GirlForm.get())
            if info_text:
                try:
                    data["form_info_message"] = await data["form_info_message"].edit_text(info_text)
                except aiogram.exceptions.MessageNotModified:
                    pass
                except Exception:
                    logger.error("Exception while editing form_info_message")
                    data["form_info_message"] = await msg.answer(info_text, disable_notification=True)

            data["prev_question_message"] = await self.send_question_message(msg, state, question_number)

    async def send_question_message(self, msg: types.Message, state: FSMContext, question_number: str):
        async with state.proxy() as data:
            handler = self.question_handlers.get(question_number)
            logger.info(f"sending {handler=}")

            if handler.type in ["text_input", "media"]:
                return await msg.answer(await handler.text(), reply_markup=GirlFormKeyboard.back())

            if handler.type == "button_choices":
                return await msg.answer(await handler.text(),
                                        reply_markup=GirlFormKeyboard.button_choices(await handler.choices(),
                                                                                     question_number))

            if handler.type == "multicheckbox":
                return await msg.answer(await handler.text(),
                                        reply_markup=GirlFormKeyboard.checkbox_choices(
                                            await handler.choices(),
                                            data.get("selected_choices", {}).get(question_number, []),
                                            question_number))

            if handler.type == "yes_no":
                return await msg.answer(await handler.text(),
                                        reply_markup=GirlFormKeyboard.button_choices(
                                            ["✅ Да", "❌ Нет"],
                                            question_number
                                        ))
