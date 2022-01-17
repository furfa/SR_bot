import asyncio

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from api.user import BackendUser


BAN_LIST = []


async def update_ban_list():
    global BAN_LIST
    while True:
        print("Hello")
        try:
            users = await BackendUser.list()
            BAN_LIST = [user.id for user in users if not user.has_access]
        except Exception:
            logger.exception("exception while getting users list")
        await asyncio.sleep(10*60)


class HasAccessMiddleware(BaseMiddleware):
    update_loop_started = False

    def init(self, *args, **kwargs):
        super(HasAccessMiddleware, self).init(*args, **kwargs)

    async def on_pre_process_message(self, message: types.Message, data: dict):
        if not self.update_loop_started:
            asyncio.create_task(update_ban_list())
            self.update_loop_started = True

        user_id = message.from_user.id
        asyncio.create_task(BackendUser.update_last_usage())

        print(BAN_LIST)
        if user_id in BAN_LIST:
            await message.answer("😡 Вы заблокированы в боте")
            raise CancelHandler()
