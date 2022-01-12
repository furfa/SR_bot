from typing import Optional

import aiohttp
from aiogram import types
from pydantic import BaseModel, parse_obj_as
from api.base import get_instance, request


class GirlFormPhoto(BaseModel):
    id: int
    is_approve: bool
    photo: str
    form: int

    @staticmethod
    async def create(photo, is_approve=False, ) -> "GirlForm":
        form = await GirlForm.get()

        data = aiohttp.formdata.FormData()
        data.add_field('form', str(form.id))
        data.add_field('is_approve', str(is_approve))
        data.add_field('photo', photo, filename=f'{form.id}.jpeg', content_type='image/jpeg')
        return await request('post', path="girl_form_photos", data=data)


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
    photos: list[GirlFormPhoto]

    @staticmethod
    async def create() -> "GirlForm":
        tg_user = types.User.get_current()
        return await get_instance(GirlForm, 'post', 'girl_forms/create_by_user/', json={
            "user":tg_user.id
        })

    @staticmethod
    async def get(tg_user_id=None) -> "GirlForm":
        if not tg_user_id:
            tg_user = types.User.get_current()
            tg_user_id = tg_user.id
        return await get_instance(GirlForm, 'get', f'girl_forms/{tg_user_id}')

    @staticmethod
    async def list(query={}) -> list["GirlForm"]:
        return await get_instance(list[GirlForm], 'get', path='girl_forms', query=query)

    @staticmethod
    async def update(tg_user_id=None, **kwargs) -> "GirlForm":
        if not tg_user_id:
            tg_user = types.User.get_current()
            tg_user_id = tg_user.id
        return await get_instance(GirlForm, 'patch', path=f'girl_forms/{tg_user_id}', json=kwargs)

    @staticmethod
    async def set_filled(**kwargs) -> "GirlForm":
        tg_user = types.User.get_current()
        return await get_instance(GirlForm, 'post', path=f'girl_forms/{tg_user.id}/set_filled/', json={})