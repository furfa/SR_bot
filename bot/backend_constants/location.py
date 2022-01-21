import multiprocessing

from api.base import request
from backend_constants.manager import multiprocessing_manager

COUNTRY_LIST = multiprocessing_manager.list()


async def update_country_list():
    COUNTRY_LIST[:] = await request("get", "location/country/")