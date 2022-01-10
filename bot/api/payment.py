import io

import aiohttp
from aiogram import types
from loguru import logger
from pydantic import BaseModel
from .base import get_instance, request


class Payment(BaseModel):
    id: int
    status: str
    user: int
    amount: float
    screenshot: str

    @staticmethod
    async def list(status) -> list["Payment"]:
        return await get_instance(list[Payment], 'get', path='payment', query={'status': status})

    @staticmethod
    async def get(id_) -> "Payment":
        return await get_instance(Payment, 'get', path=f'payment/{id_}')

    @staticmethod
    async def create(screenshot: io.BytesIO, amount: float) -> "Payment":

        current_user = types.User.get_current()

        data = aiohttp.formdata.FormData()
        data.add_field('user', str(current_user.id))
        data.add_field('amount', str(amount))
        data.add_field('screenshot', screenshot, filename=f'{current_user.id}.jpeg', content_type='image/jpeg')
        return await request('post', path=f"payment", data=data)

    @staticmethod
    async def update(id_, **kwargs) -> "Payment":
        return await get_instance(Payment, 'patch', path=f'payment/{id_}', json=kwargs)