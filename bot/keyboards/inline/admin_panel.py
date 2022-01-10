from aiogram import types

from .consts import InlineConstructor
from aiogram.utils.callback_data import CallbackData
from .callbacks import AdminQuestionAnswer


class AdminQuestionInline(InlineConstructor):
    answer_callback_data = CallbackData("AdminQuestionInline", "id")
    approve_screenshot_callback_data = CallbackData("ApproveScreen", "id", "type")

    @staticmethod
    def answer(id):
        schema = [1]
        actions = [
            {'text': 'Ответить', 'callback_data': ({"id": id}, AdminQuestionAnswer)}
        ]
        return AdminQuestionInline._create_kb(actions, schema)

    @staticmethod
    def approve_screenshot(id):
        schema = [2]
        actions = [
            {'text': '✅ Подтвердить',
             'callback_data': ({"id": id, "type":"approve"}, AdminQuestionInline.approve_screenshot_callback_data)},
            {'text': '❌ Отклонить',
             'callback_data': ({"id": id, "type": "reject"}, AdminQuestionInline.approve_screenshot_callback_data)}
        ]
        return AdminQuestionInline._create_kb(actions, schema)