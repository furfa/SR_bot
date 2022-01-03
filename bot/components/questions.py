from typing import Callable

from aiogram.utils.callback_data import CallbackData
from aiogram import types, Bot, Dispatcher

from components.base import BaseComponent


class TextQuestion(BaseComponent):
    def __init__(self, *, question_text, on_back: Callable, **kwargs):
        """
        :param on_back: callback при нажатии кнопки назад в стейте компонента
        """
        super().__init__(**kwargs)
        self.on_back = on_back
        self.question = question_text

    def setup(self, dp: Dispatcher):
        dp.register_message_handler(self.back, text=["К предыдущему вопросу"])

    async def enter(self):
        bot = Bot.get_current()
        user = types.User.get_current()
        await self.states.entered.set()
        await bot.send_message(user.id, self.question)

    def validate_answer(self, text):
        return True

    async def answer(self, msg: types.Message):

        if not self.validate_answer(msg.text):
            await msg.answer("Некорректный ввод, напишите еще раз")
            return

        await self.on_success(msg.text)
        await self.on_next()

    async def back(self, msg: types.Message):
        await self.states.finish()
        await msg.answer("⬅️ Возвращаюсь назад")
        await self.on_back()
