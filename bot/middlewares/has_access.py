from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from api.user import BackendUser


class HasAccessMiddleware(BaseMiddleware):

    def init(self, *args, **kwargs):
        super(HasAccessMiddleware, self).init(*args, **kwargs)

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        try:
            be = await BackendUser.update_last_usage()
        except Exception as e:
            logger.exception("error while getting user")
            return

        if not be.has_access:
            await message.answer("😡 Вы заблокированы в боте")
            raise CancelHandler()