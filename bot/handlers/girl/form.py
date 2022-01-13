import asyncio
import re
from io import BytesIO

import aiogram
from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram import exceptions
from aiogram.utils.callback_data import CallbackData
from loguru import logger

from api.base import request
import api.girl_form
from keyboards.inline.consts import InlineConstructor
from states.girl.form import GirlFormStates, GirlFormNameStates, GirlFormPriceStates


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


class GirlFormBase:

    def __init__(self, enter_state, need_approve):
        self.enter_state = enter_state
        self.need_approve = need_approve
        self.question_handlers = {}

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

    def get_start_node(self):
        return [key for key, handler in self.question_handlers.items() if handler["prev"] == "ENTER"][0]

    async def button_choices_query_handler(self, query: types.CallbackQuery, state: FSMContext, callback_data: dict):
        question_num = callback_data["question_num"]
        option_num = int(callback_data["option_num"])
        if self.question_handlers[question_num]["type"] in ("button_choices", "city_button_choices"):
            choices = self.question_handlers[question_num]["choices"]
        elif self.question_handlers[question_num]["type"] == "yes_no":
            choices = [True, False]
        else:
            logger.error("not allowed action")
            return
        choice = choices[option_num]

        if question_num and not await self.validate_answer(choice, question_num):
            await query.message.answer("Неверный формат, введите еще раз", reply_markup=GirlFormKeyboard.back())
            return

        await query.message.edit_text(query.message.text)
        if self.question_handlers[question_num]["type"] == "yes_no":
            await query.message.answer(f"👉 {'Да' if choice else 'Нет'}")
            async with state.proxy() as data:
                data['question_number'] = self.question_handlers[question_num]["yes_next" if choice else "no_next"]
            await self.process_answer(state=state, question_number=question_num, choice=choice)
            await self.send_question(query.message, state, incremented=True)
        else:
            await query.message.answer(f"👉 {choice}")
            await self.process_answer(state=state, question_number=question_num, choice=choice)
            await self.send_question(query.message, state, incremented=False)

    async def checkbox_choices_query_handler(self, query: types.CallbackQuery, state: FSMContext, callback_data: dict):
        async with state.proxy() as data:
            question_num = callback_data["question_num"]

            if self.question_handlers[question_num]["type"] != "multicheckbox":
                logger.error("not allowed action")
                return
            data["selected_choices"] = data.get("selected_choices", {})
            data["selected_choices"][question_num] = data["selected_choices"].get(question_num, [])

            if callback_data["option_num"] == "save":
                question_text = self.question_handlers[question_num]["text"]
                selected_choices = [self.question_handlers[question_num]["choices"][choice_index] for choice_index in
                                    data["selected_choices"][question_num]]
                res_str = "\n".join(
                    "🔹 " + choice for choice in selected_choices)
                await query.message.delete()
                await query.message.answer(question_text + "\n\n<b>Выбрано:</b> \n" + res_str)
                await self.process_answer(state=state, question_number=question_num, choice=selected_choices)
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
            data['question_number'] = data.get('question_number', self.get_start_node())
            data['question_number'] = self.question_handlers[data['question_number']]["prev"]
            if data['question_number'] != "ENTER":
                data['question_number'] = self.question_handlers[data['question_number']]["prev"]
            await query.message.delete()
            question_number = data['question_number']
        logger.error(f"{question_number=}")
        if question_number == "ENTER":
            await state.finish()
            await query.message.answer("Выхожу из анкеты ❌")
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

        warning = "⛔️ Неверный формат, введите еще раз"
        if not msg.photo or (question_number and self.question_handlers[question_number]["type"] != "media"):
            if pqm := data.get("prev_question_message"):
                # resend message
                await pqm.delete()
                new_text = ("" if warning in pqm.text else "<b>" + warning + "</b>\n") + pqm.text
                data["prev_question_message"] = await pqm.answer(
                    new_text,
                    reply_markup=pqm.reply_markup
                )
                await msg.delete()
            else:
                await msg.answer("<b>" + warning + "</b>", reply_markup=GirlFormKeyboard.back())
            return

        print(f"{msg=} {question_number=}")
        await self.process_answer(msg, state, question_number)
        await self.send_question(msg, state)

    async def message_handler(self, msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            logger.info(f"{dict(data)= } {msg=}")
            question_number = data.get('question_number')
            print(f"{question_number=}")

            warning = "⛔️ Неверный формат, введите еще раз"
            if (
                    question_number and (
                        self.question_handlers[question_number]["type"] != "text_input" or
                        not await self.validate_answer(msg.text, question_number)
                    )
            ):
                if pqm := data.get("prev_question_message"):
                    # resend message
                    await pqm.delete()
                    new_text = ("" if warning in pqm.text else "<b>"+warning+"</b>\n") + pqm.text
                    data["prev_question_message"] = await pqm.answer(
                        new_text,
                        reply_markup=pqm.reply_markup
                    )
                    await msg.delete()
                else:
                    await msg.answer("<b>"+warning+"</b>", reply_markup=GirlFormKeyboard.back())
                return

        await self.process_answer(msg, state, question_number)
        await self.send_question(msg, state)

    async def send_question(self, msg: types.Message, state: FSMContext, incremented=False):
        async with state.proxy() as data:
            if not incremented:
                if not data.get('question_number') is None:
                    data['question_number'] = self.question_handlers[data['question_number']]["next"]
                else:
                    data['question_number'] = self.get_start_node()
                    await self.enter_state.set()

            question_number = data['question_number']
            try:
                if pqm := data.get("prev_question_message"):
                    await pqm.edit_text(pqm.text)  # delete inline buttons
            except (exceptions.MessageNotModified, exceptions.MessageToEditNotFound) as e:
                logger.error("error while deleting markup")

        if question_number == "EXIT":
            await state.finish()
            await msg.answer("Анкета заполнена ✅")
            if self.need_approve:
                await api.girl_form.GirlForm.set_filled()
            return

        async with state.proxy() as data:
            data['prev_question_message'] = await self.send_question_message(msg, state, question_number)

    async def send_question_message(self, msg: types.Message, state: FSMContext, question_number: int):
        async with state.proxy() as data:
            handler = self.question_handlers[question_number]

            if handler["type"] in ["text_input", "media"]:
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
            if handler["type"] == "city_button_choices":
                gf = await api.girl_form.GirlForm.get()
                selected_cities = None
                for country in self.country_list:
                    if country["id"] == gf.country:
                        selected_cities = country["cities"]
                if not selected_cities:
                    selected_cities = self.city_list

                return await msg.answer(handler["text"],
                                        reply_markup=GirlFormKeyboard.button_choices(
                                            [city["name"] for city in selected_cities],
                                            question_number
                                        ))

    async def validate_answer(self, text: str, question_number: str):
        if handler := self.question_handlers.get(question_number):
            return handler["validators"](text)

    async def process_answer(self, msg: types.Message = None, state: FSMContext = None, question_number: str = None,
                             choice=None):
        if handler := self.question_handlers.get(question_number):
            await handler["processor"](msg, choice)


class GirlChangeName(GirlFormBase):
    @classmethod
    async def create(cls):
        self = GirlForm(enter_state=GirlFormNameStates.entered, need_approve=False)

        self.question_handlers = {
            "name": {
                "type": "text_input",
                "text": "Укажите, пожалуйста, вашe имя!",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("name"),
                "next": "EXIT",
                "prev": "ENTER"
            },
        }
        return self

    async def empty(self, msg, choice):
        return None

    def additional_data_factory(self, key):
        async def inner(msg, choice):
            gf = await api.girl_form.GirlForm.get()
            gf.additional_data[key] = choice if choice else msg.text
            await api.girl_form.GirlForm.update(additional_data=gf.additional_data)
        return inner


class GirlChangePrice(GirlFormBase):
    @classmethod
    async def create(cls):
        self = GirlForm(enter_state=GirlFormPriceStates.entered, need_approve=False)

        self.question_handlers = {
            "sponsorship_relations": {
                "type": "yes_no",
                "text": "Вас интересуют спонсорские отношения?",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("sponsorship_relations"),
                "yes_next": "finance_support",
                "no_next": "short",
                "prev": "ENTER"
            },
            "finance_support": {
                "type": "text_input",
                "text": "Какую финансовую поддержку вы хотели бы получать от мужчины в месяц в рублях?   (Пожалуйста, адекватно оценивайте свою внешность, от этого напрямую зависит сумма обеспечения девушки)",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("finance_support"),
                "next": "short",
                "prev": "sponsorship_relations"
            },
            "short": {
                "type": "yes_no",
                "text": "Интересуют короткие свидания с вознаграждением?",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("short"),
                "yes_next": "short_amount",
                "no_next": "EXIT",
                "prev": "sponsorship_relations"
            },
            "short_amount": {
                "type": "text_input",
                "text": "Какую сумму вы хотели бы получать за встречу 2-3 часа с адекватным мужчиной? (Укажите сумму в рублях)",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("short_amount"),
                "next": "EXIT",
                "prev": "short"
            },
        }
        return self

    async def empty(self, msg, choice):
        return None

    def additional_data_factory(self, key):
        async def inner(msg, choice):
            gf = await api.girl_form.GirlForm.get()
            gf.additional_data[key] = choice if choice else msg.text
            await api.girl_form.GirlForm.update(additional_data=gf.additional_data)
        return inner


class GirlForm(GirlFormBase):
    @classmethod
    async def create(cls):
        self = GirlForm(enter_state=GirlFormStates.entered, need_approve=True)
        self.country_list = await request("get", "location/country/")
        self.city_list = []
        for country in self.country_list:
            self.city_list.extend(country["cities"])
        print(self.city_list)

        self.question_handlers = {
            "country": {
                "type": "button_choices",
                "choices": [country["name"] for country in self.country_list],
                "text": "Укажите, пожалуйста, вашу страну!",
                "validators": lambda x: True,
                "processor": self.country_processor,
                "next": "city",
                "prev": "ENTER"
            },
            "city": {
                "type": "city_button_choices",
                "choices": [city["name"] for city in self.city_list],
                "text": "Укажите, пожалуйста, ваш город проживания!",
                "validators": lambda x: True,
                "processor": self.city_processor,
                "next": "name",
                "prev": "country"
            },
            "name": {
                "type": "text_input",
                "text": "Укажите, пожалуйста, вашe имя!",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("name"),
                "next": "age",
                "prev": "city"
            },
            "age": {
                "type": "text_input",
                "text": "Укажите, пожалуйста, ваш возраст!",
                "validators": lambda x: re.fullmatch(r"\d+", x),
                "processor": self.additional_data_factory("age"),
                "next": "params",
                "prev": "name"
            },
            "params": {
                "type": "text_input",
                "text": "Укажите, пожалуйста, ваши параметры!\n\n 90/60/90",
                "validators": lambda x: re.fullmatch(r"\d+/\d+/\d+", x),
                "processor": self.additional_data_factory("body_params"),
                "next": "nationality",
                "prev": "age"
            },
            "nationality": {
                "type": "button_choices",
                "choices": [country["name"] for country in self.country_list],
                "text": "Укажите, пожалуйста, вашу национальность!",
                "validators": lambda x: True,
                "processor": self.nationality_processor,
                "next": "sponsorship_relations",
                "prev": "params"
            },
            "sponsorship_relations": {
                "type": "yes_no",
                "text": "Вас интересуют спонсорские отношения?",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("sponsorship_relations"),
                "yes_next": "finance_support",
                "no_next": "married_relations",
                "prev": "nationality"
            },
            "finance_support": {
                "type": "text_input",
                "text": "Какую финансовую поддержку вы хотели бы получать от мужчины в месяц в рублях?   (Пожалуйста, адекватно оценивайте свою внешность, от этого напрямую зависит сумма обеспечения девушки)",
                "validators": lambda x: re.fullmatch(r"\d+", x),
                "processor": self.additional_data_factory("finance_support"),
                "next": "married_relations",
                "prev": "sponsorship_relations"
            },
            "married_relations": {
                "type": "yes_no",
                "text": "Рассматриваете ли вы отношения на материальной основе с женатыми мужчинами?",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("married_relations"),
                "yes_next": "abroad",
                "no_next": "abroad",
                "prev": "finance_support"
            },
            "abroad": {
                "type": "yes_no",
                "text": "Рассматриваете ли вы поездки с мужчиной за границу?",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("abroad"),
                "yes_next": "documents",
                "no_next": "short",
                "prev": "married_relations"
            },
            "documents": {
                "type": "multicheckbox",
                "text": "Что у вас имеется в наличии из документов?",
                "choices": [
                    "Только загран паспорт",
                    "Виза Шенген",
                    "Виза Англия",
                    "Виза США"
                ],
                "validators": lambda x: True,
                "processor": self.additional_data_factory("documents"),
                "next": "short",
                "prev": "abroad"
            },
            "short": {
                "type": "yes_no",
                "text": "Интересуют короткие свидания с вознаграждением?",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("short"),
                "yes_next": "short_amount",
                "no_next": "about",
                "prev": "abroad"
            },
            "short_amount": {
                "type": "text_input",
                "text": "Какую сумму вы хотели бы получать за встречу 2-3 часа с адекватным мужчиной? (Укажите сумму в рублях)",
                "validators": lambda x: re.fullmatch(r"\d+", x),
                "processor": self.additional_data_factory("short_amount"),
                "next": "about",
                "prev": "short"
            },
            "about": {
                "type": "text_input",
                "text": "Расскажите немного о себе:\nОбразование, увлечения, хобби",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("about"),
                "next": "sex",
                "prev": "short"
            },
            "sex": {
                "type": "text_input",
                "text": "Расскажите о своих предпочтениях в сексе, желаниях, запретах, часто мужчине это очень важно.\n Напишите минус(-) для пропуска.",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("sex"),
                "next": "work_phone_number",
                "prev": "about"
            },
            "work_phone_number": {
                "type": "text_input",
                "text": "Укажите ваш рабочий номер телефона",
                "validators": lambda x: re.fullmatch(r"\+?\d+", x),
                "processor": self.additional_data_factory("work_phone_number"),
                "next": "whatsapp_number",
                "prev": "sex"
            },
            "whatsapp_number": {
                "type": "text_input",
                "text": "Отправьте ваш номер whatsapp, или минус для пропуска",
                "validators": lambda x: True,
                "processor": self.additional_data_factory("whatsapp_number"),
                "next": "verification_photo",
                "prev": "work_phone_number"
            },
            "verification_photo": {
                "type": "media",
                "text": "Для того, чтобы найти Вам мужчину мы должны убедится в том, что это ваши фотографии. \nОтправьте пожалуйста в чат ваше селфи с лицом и жестом 🤞🏾, для верификации. \nПроверка проводится роботом, после подтверждения личности ваше фото удаляется из базы данных.\n Для вашего удобства и безопасности, мы боремся за то, чтобы все участники были реальными людьми.\n Спасибо за понимание! Удачных знакомств...♥️",
                "validators": lambda x: True,
                "processor": self.photo_factory(is_approve=True),
                "next": "add_photo",
                "prev": "whatsapp_number"
            },
            "add_photo": {
                "type": "yes_no",
                "text": "Пришлите Ваши фото и видео.\nМужчинам уже давно не интересны профессиональные фото, зачастую от того, что девушки часто в жизни выглядят совсем иначе, поэтому просим Вас быть предельно честной. \nПеречень фото, которые нужно предоставить:\n▫️ Фото или видео лица/селфи (минимум макияжа и фильтров)\n▫️ Фигура с разных ракурсов, в полный рост, в обтягивающей одежде или купальнике, где хорошо будут видны: грудь, ягодицы, ноги, живот.\▫️ Разрешается прикрепить несколько фото со студийных съёмок ▫️ Всего не более 10 фото или видео\nСовет. Если хотите найти достойного мужчину, то потратьте 20 минут своего времени и снимите новые фото. \nЕсли они не будут подходить, то Ваша анкета не пройдёт модерацию и наша администрация сообщит Вам об этом.\n Добавляем фото?",
                "validators": lambda x: True,
                "processor": self.empty,
                "yes_next": "wait_photo",
                "no_next": "EXIT",
                "prev": "verification_photo"
            },
            "wait_photo": {
                "type": "media",
                "text": "Жду фото",
                "validators": lambda x: True,
                "processor": self.photo_factory(is_approve=False),
                "next": "add_photo",
                "prev": "add_photo"
            },
        }
        return self

    async def empty(self, msg, choice):
        return None

    async def country_processor(self, msg, choice):
        for i in self.country_list:
            if i["name"] == choice:
                await api.girl_form.GirlForm.update(country=i["id"])

    async def city_processor(self, msg, choice):
        for i in self.city_list:
            if i["name"] == choice:
                await api.girl_form.GirlForm.update(city=i["id"])

    def additional_data_factory(self, key):
        async def inner(msg, choice):
            gf = await api.girl_form.GirlForm.get()
            gf.additional_data[key] = choice if choice is not None else msg.text
            await api.girl_form.GirlForm.update(additional_data=gf.additional_data)
        return inner

    async def nationality_processor(self, msg, choice):
        for i in self.country_list:
            if i["name"] == choice:
                await api.girl_form.GirlForm.update(nationality=i["id"])

    def photo_factory(self, **kwargs):
        async def inner(msg: types.Message, choice):
            bot = Bot.get_current()
            downloaded = await bot.download_file_by_id(msg.photo[-1].file_id)
            b = BytesIO()
            b.write(downloaded.getvalue())
            b.seek(0)
            await api.girl_form.GirlFormPhoto.create(b, **kwargs)
        return inner