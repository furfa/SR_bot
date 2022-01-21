from aiogram import types


class ChatHistoryState:
    def __init__(self):
        self.history = {}

    async def set(self, user_id, message_order):
        self.history[user_id] = message_order

    async def get(self, user_id) -> list[types.Message]:
        return self.history.get(user_id, [])

    async def append(self, user_id, message):
        user_hist = await self.get(user_id)
        user_hist.append(message)
        await self.set(user_id, user_hist)


CHAT_HISTORY = ChatHistoryState()