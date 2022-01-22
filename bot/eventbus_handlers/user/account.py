from loguru import logger
from aiogram import Bot, Dispatcher

from base.aiogram_utils import memorize_send_message
from templates.user.account import ADMIN_NEW_SCREENSHOT, SCREENSHOT_APPROVE, SCREENSHOT_REJECT


async def new_payment_screenshot(bot: Bot, body):
    admin_id = body.get("admin_id")
    if not admin_id:
        return True
    await memorize_send_message(bot, admin_id, ADMIN_NEW_SCREENSHOT)
    return True


async def payment_screenshot_processed(bot: Bot, body):
    text = ""
    if body["status"] == "APPROVED":
        text = SCREENSHOT_APPROVE.format(amount=body["amount"])
    if body["status"] == "REJECTED":
        text = SCREENSHOT_REJECT.format(amount=body["amount"])

    await memorize_send_message(bot, body["user"], text)
    return True