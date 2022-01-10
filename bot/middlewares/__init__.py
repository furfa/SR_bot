from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware
from .has_access import HasAccessMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(HasAccessMiddleware())
