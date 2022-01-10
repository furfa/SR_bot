from typing import Optional
from aiogram import types
from pydantic import BaseModel, parse_obj_as
from api.base import get_instance, request


class GirlForm(BaseModel):
    id: int
    country: Optional[int]
    city: Optional[int]
    nationality: Optional[int]
    user: int
    additional_data: dict

    @staticmethod
    async def get() -> "GirlForm":
        tg_user = types.User.get_current()
        return await get_instance(GirlForm, 'get', f'girl_forms/{tg_user.id}')

    @staticmethod
    async def list() -> list["GirlForm"]:
        return await get_instance(list[GirlForm], 'get', path='girl_forms')

    @staticmethod
    async def update(**kwargs) -> "GirlForm":
        tg_user = types.User.get_current()
        return await get_instance(GirlForm, 'patch', path=f'girl_forms/{tg_user.id}', json=kwargs)