from typing import Optional
from aiogram import types
from pydantic import BaseModel, parse_obj_as
from api.base import get_instance, request


class GirlForm(BaseModel):
    id: int
    status: str
    country: Optional[int]
    city: Optional[int]
    nationality: Optional[int]
    user: int
    additional_data: dict
    has_top_status: bool
    price: Optional[float]

    @staticmethod
    async def create() -> "GirlForm":
        tg_user = types.User.get_current()
        return await get_instance(GirlForm, 'post', 'girl_forms/create_by_user/', json={
            "user":tg_user.id
        })

    @staticmethod
    async def get(tg_user_id = None) -> "GirlForm":
        if not tg_user_id:
            tg_user = types.User.get_current()
            tg_user_id = tg_user.id
        return await get_instance(GirlForm, 'get', f'girl_forms/{tg_user_id}')

    @staticmethod
    async def list(query={}) -> list["GirlForm"]:
        return await get_instance(list[GirlForm], 'get', path='girl_forms', query=query)

    @staticmethod
    async def update(tg_user_id, **kwargs) -> "GirlForm":
        if not tg_user_id:
            tg_user = types.User.get_current()
            tg_user_id = tg_user.id
        return await get_instance(GirlForm, 'patch', path=f'girl_forms/{tg_user_id}', json=kwargs)

    @staticmethod
    async def set_filled(**kwargs) -> "GirlForm":
        tg_user = types.User.get_current()
        return await get_instance(GirlForm, 'post', path=f'girl_forms/{tg_user.id}/set_filled/', json={})
