from aiogram import types

from .consts import InlineConstructor
from aiogram.utils.callback_data import CallbackData
from .callbacks import AdminQuestionAnswer

class AdminQuestionInline(InlineConstructor):

    answer_callback_data = CallbackData("AdminQuestionInline", "id")
    @staticmethod
    def answer(id):
        schema = [1]
        actions = [
            {'text': 'Ответить', 'callback_data': ({"id":id}, AdminQuestionAnswer) }
        ]
        return AdminQuestionInline._create_kb(actions, schema)