from loguru import logger
from aiogram import Bot, Dispatcher

from api.user import UserSupportQuestion
from base.aiogram_utils import memorize_send_message
from templates.admin.admin_panel import ADMIN_NOTIFICATION
from templates.user.support import QUESTION_ANSWERED


async def question_created(bot: Bot, body):
    admin_id = body.get("admin_id")
    if not admin_id:
        return True
    await memorize_send_message(bot, admin_id, ADMIN_NOTIFICATION)
    return True


async def question_answered(bot: Bot, body):
    changed = UserSupportQuestion.parse_obj(body)

    await memorize_send_message(
        bot,
        changed.user,
        QUESTION_ANSWERED.format(question=changed.question_body, answer=changed.answer_body)
    )

    return True