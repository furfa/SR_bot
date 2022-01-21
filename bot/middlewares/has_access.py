import asyncio

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from api.user import BackendUser
from backend_constants.ban_list import BAN_LIST


class HasAccessMiddleware(BaseMiddleware):

    def init(self, *args, **kwargs):
        super(HasAccessMiddleware, self).init(*args, **kwargs)

    async def on_pre_process_message(self, message: types.Message, data: dict):

        user_id = message.from_user.id
        asyncio.create_task(BackendUser.update_last_usage())

        print(BAN_LIST)
        if user_id in BAN_LIST:
            await message.answer("😡 Вы заблокированы в боте")
            raise CancelHandler()
