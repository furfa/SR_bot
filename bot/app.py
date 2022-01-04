import sys
from typing import List, Tuple
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiohttp import web
from loguru import logger

from utils.logging_to_loguru import setup_loguru
from utils.eventbus_listener import EventbusListener
import config

bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML, validate_token=True)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
eventbus_listener = EventbusListener(bot)


async def on_startup(dp):
    import middlewares
    import handlers
    import eventbus_handlers

    eventbus_handlers.setup(eventbus_listener)
    middlewares.setup(dp)
    handlers.errors.setup(dp)
    handlers.user.setup(dp)
    handlers.admin.setup(dp)
    handlers.girl.setup(dp)


@logger.catch()
async def main():
    setup_loguru()
    # logger.remove()
    # logger.add(sys.stderr, level="INFO")
    await on_startup(dp)

    asyncio.create_task(eventbus_listener.start_pooling())
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())