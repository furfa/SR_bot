from aiogram import types

from .consts import InlineConstructor
from aiogram.utils.callback_data import CallbackData
from .callbacks import AdminQuestionAnswer


class SrMenuInline(InlineConstructor):
    form_callback_data = CallbackData("FormMenu")
    back_to_secret_room = CallbackData("BackSecretRoom")
    fill_form = CallbackData("FillForm")
    delete_form = CallbackData("DeleteForm")
    change_name = CallbackData("ChangeFormName")
    change_price = CallbackData("ChangePrice")

    @staticmethod
    def menu():
        schema = [1]
        actions = [
            {'text': 'Моя анкета', 'callback_data': ({}, SrMenuInline.form_callback_data)},
        ]
        return SrMenuInline._create_kb(actions, schema)

    @staticmethod
    def ask_to_create_form():
        schema = [1, 1]
        actions = [
            {'text': 'Заполнить', 'callback_data': ({}, SrMenuInline.fill_form)},
            {'text': '🔙 Назад', 'callback_data': ({}, SrMenuInline.back_to_secret_room)}
        ]
        return SrMenuInline._create_kb(actions, schema)

    @staticmethod
    def only_back():
        schema = [1]
        actions = [
            {'text': '🔙 Назад', 'callback_data': ({}, SrMenuInline.back_to_secret_room)}
        ]
        return SrMenuInline._create_kb(actions, schema)

    @staticmethod
    def form_menu():
        schema = [2,1,1,1]
        actions = [
            {'text': '🔵 Изменить имя', 'callback_data': ({}, SrMenuInline.change_name)},
            {'text': '🔴 Изменить прайс', 'callback_data': ({}, SrMenuInline.change_price)},
            {'text': '❌ Удалить', 'callback_data': ({}, SrMenuInline.delete_form)},
            {'text': 'Заполнить анкету заново', 'callback_data': ({}, SrMenuInline.fill_form)},
            {'text': '🔙 Назад', 'callback_data': ({}, SrMenuInline.back_to_secret_room)}
        ]
        return SrMenuInline._create_kb(actions, schema)