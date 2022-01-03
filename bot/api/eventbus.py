from pydantic import BaseModel, parse_obj_as
from . base import get_instance, request


class Event(BaseModel):
    pk         : int
    body       : str
    event_type : str

    @staticmethod
    async def get():
        return await get_instance(list[Event], 'get', 'event_bus')

    @staticmethod
    async def delete(pk : int):
        return await request('delete', f'event_bus/{pk}/')