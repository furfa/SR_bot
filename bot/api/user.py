from aiogram import types
from loguru import logger
from pydantic import BaseModel
from .base import get_instance, request


class BackendUser(BaseModel):
    id: int
    has_access: bool
    is_admin: bool
    language: str
    sex: str
    balance: float

    @staticmethod
    async def list():
        return await get_instance(list[BackendUser], 'get', path='users')

    @staticmethod
    async def create():
        tg_user = types.User.get_current()
        data = {
            'id': tg_user.id
        }
        return await get_instance(BackendUser, 'post', path='users', json=data)

    @staticmethod
    async def get() -> "BackendUser":
        tg_user = types.User.get_current()
        return await get_instance(BackendUser, 'get', path=f'users/{tg_user.id}')

    @staticmethod
    async def update(**kwargs):
        tg_user = types.User.get_current()
        return await get_instance(BackendUser, 'patch', path=f'users/{tg_user.id}', json=kwargs)

    @staticmethod
    async def check_is_admin():
        b_user = await BackendUser.get()
        return b_user.is_admin

    @staticmethod
    async def update_last_usage():
        tg_user = types.User.get_current()
        return await get_instance(BackendUser, 'patch', path=f'users/{tg_user.id}/update_last_usage', json={})


class UserSupportQuestion(BaseModel):
    id: int
    user: int
    question_body: str
    answer_body: str
    status: str
    type: str

    @staticmethod
    async def list(type_filter):
        return await get_instance(list[UserSupportQuestion], 'get', path='support_question', query={'type': type_filter})

    @staticmethod
    async def create(question_body, type):
        tg_user = types.User.get_current()
        data = {
            'user': tg_user.id,
            'question_body': question_body,
            'type': type
        }
        return await get_instance(UserSupportQuestion, 'post', path='support_question', json=data)

    @staticmethod
    async def update(id_, **kwargs) -> "UserSupportQuestion":
        return await get_instance(UserSupportQuestion, 'patch', path=f'support_question/{id_}', json=kwargs)
