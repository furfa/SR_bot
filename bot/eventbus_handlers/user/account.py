from loguru import logger
from aiogram import Bot, Dispatcher

from templates.user.account import ADMIN_NEW_SCREENSHOT, SCREENSHOT_APPROVE, SCREENSHOT_REJECT


async def new_payment_screenshot(bot: Bot, body):
    admin_id = body.get("admin_id")
    if not admin_id:
        return True
    await bot.send_message(admin_id, ADMIN_NEW_SCREENSHOT)
    return True


async def payment_screenshot_processed(bot: Bot, body):
    text = ""
    if body["status"] == "APPROVED":
        text = SCREENSHOT_APPROVE.format(amount=body["amount"])
    if body["status"] == "REJECTED":
        text = SCREENSHOT_REJECT.format(amount=body["amount"])

    await bot.send_message(body["user"], text)
    return True