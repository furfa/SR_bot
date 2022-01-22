from loguru import logger
from aiogram import Bot, Dispatcher

from api.girl_form import GirlForm
from base.aiogram_utils import memorize_send_message
from templates.girl.secret_room import FORM_ADMIN_NOTIFICATION, FORM_STATUS_UPDATED


async def new_form(bot: Bot, body):
    admin_id = body.get("admin_id")
    if not admin_id:
        return True
    await memorize_send_message(bot, admin_id, FORM_ADMIN_NOTIFICATION)
    return True


async def form_status_updated(bot: Bot, body):
    gf = GirlForm.parse_obj(body)
    await memorize_send_message(bot, gf.user, FORM_STATUS_UPDATED)
    return True