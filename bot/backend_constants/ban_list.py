import multiprocessing

from loguru import logger

from api.user import BackendUser
from backend_constants.manager import multiprocessing_manager

BAN_LIST = multiprocessing_manager.list()


async def update_ban_list():
    try:
        users = await BackendUser.list()
        BAN_LIST[:] = [user.id for user in users if not user.has_access]
    except Exception:
        logger.exception("exception while getting users list")