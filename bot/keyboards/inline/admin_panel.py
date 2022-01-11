from aiogram import types

from .consts import InlineConstructor
from aiogram.utils.callback_data import CallbackData
from .callbacks import AdminQuestionAnswer


class AdminQuestionInline(InlineConstructor):
    answer_callback_data = CallbackData("AdminQuestionInline", "id")
    approve_screenshot_callback_data = CallbackData("ApproveScreen", "id", "type")
    form_select_callback_data = CallbackData("FormSelect", "type")

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

    @staticmethod
    def form_select():
        schema = [1,1,1]
        actions = [
            {'text': 'На проверке',
             'callback_data': ({"type": "FILLED"}, AdminQuestionInline.form_select_callback_data)},
            {'text': 'Сомнительные',
             'callback_data': ({"type": "REJECTED"}, AdminQuestionInline.form_select_callback_data)},
            {'text': 'Подтвержденные',
             'callback_data': ({"type": "CONFIRMED"}, AdminQuestionInline.form_select_callback_data)}
        ]
        return AdminQuestionInline._create_kb(actions, schema)