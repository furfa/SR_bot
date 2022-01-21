from __future__ import annotations

from io import BytesIO
from typing import Union

from aiogram import Bot
from loguru import logger

from api.base import request
import api.girl_form
import asyncio


def additional_data_factory(key):
    async def inner(msg, choice):
        asyncio.create_task(api.girl_form.GirlForm.update_additional_data_key(key, choice if choice is not None else msg.text))
    return inner


class QuestionTree:
    def __init__(self):
        self.tree = {}
        self.start_node = None

    @staticmethod
    def from_nodes(*list_nodes):
        qt = QuestionTree()
        for node in list_nodes:
            qt.add(node)
        return qt

    def add(self, question: BaseQuestion):
        question.set_question_list(self)
        if question.prev_id == "ENTER":
            self.start_node = question
        self.tree[question.question_id] = question

    def get(self, question_id) -> Union[BaseQuestion, TextQuestion, ChoicesQuestion]:
        logger.info(f"getting {question_id=}")
        return self.tree.get(question_id)

    def get_start(self):
        if not self.start_node:
            raise ValueError("No start node")
        return self.start_node.question_id


class BaseQuestion:
    question_id = "some_id"
    type = "text_input"
    question_text = "Some text"
    question_list = None

    def __init__(self, next_id, prev_id):
        self.next_id = next_id
        self.prev_id = prev_id

    def set_question_list(self, question_list):
        self.question_list = question_list

    async def text(self):
        return self.question_text

    async def validator(self, text):
        print("validating", text)
        return True

    async def processor(self, msg, choice):
        df = additional_data_factory(self.question_id)
        return await df(msg, choice)

    async def next(self):
        return self.next_id

    async def prev(self):
        return self.prev_id


class TextQuestion(BaseQuestion):
    type = "text_input"


class MediaQuestion(TextQuestion):
    type = "media"
    is_approve = False

    async def processor(self, msg, choice):
        bot = Bot.get_current()
        downloaded = await bot.download_file_by_id(msg.photo[-1].file_id)
        b = BytesIO()
        b.write(downloaded.getvalue())
        b.seek(0)
        asyncio.create_task(api.girl_form.GirlFormPhoto.create(b, is_approve=self.is_approve))


class ChoicesQuestion(BaseQuestion):
    type = "button_choices"

    async def choices(self):
        return ["Опция 1", "Опция 2"]


class BinaryQuestion(ChoicesQuestion):
    type = "button_choices"

    async def choices(self):
        return ["✅ Да", "❌ Нет"]

    async def processor(self, msg, choice):
        df = additional_data_factory(self.question_id)
        return await df(msg, choice=="✅ Да")


class MulticheckboxQuestion(BaseQuestion):
    type = "multicheckbox"

    async def choices(self):
        return ["Опция 1", "Опция 2"]
