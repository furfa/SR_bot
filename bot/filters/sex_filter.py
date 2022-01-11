from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from api.user import BackendUser


class SexFilter(BoundFilter):
    key = 'is_girl'

    def __init__(self, is_girl):
        self.is_girl = is_girl

    async def check(self, message: Message):
        be = await BackendUser.get(message.from_user)
        if be.sex == "UNKNOWN":
            return False
        girl = (be.sex == "GIRL")

        if girl == self.is_girl:
            return True
        return False
    