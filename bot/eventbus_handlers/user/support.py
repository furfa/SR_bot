from loguru import logger
from aiogram import Bot, Dispatcher

from templates.admin.admin_panel import ADMIN_NOTIFICATION


async def question_answered(bot: Bot, body):
    admin_id = body.get("admin_id")
    if not admin_id:
        return True
    await bot.send_message(admin_id, ADMIN_NOTIFICATION)
    return True