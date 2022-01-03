from typing import Callable

from aiogram import Bot
from aiogram.dispatcher.filters.state import State, StatesGroup


class BaseComponentState(StatesGroup):
    """
    Класс базовых состояний компонента
    """
    entered = State()


def state_factory(BaseClass, name):
    """
        Создает класс с именем name
    """
    class NewClass(BaseClass): pass
    NewClass.__name__ = f"{name}"
    return NewClass


class BaseComponent:
    """
        Базовый компонент
    """
    def __init__(self, *, state_base_name: str, on_success: Callable, on_next: Callable):
        """
        :param state_base_name: имя stategroup экземпляра компонента
        :param on_success: callback при получении данных от пользователя (в колбэке пишем работу с backend)
        :param on_next: callback при завершении стейта компонента (в колбэке пишем переход в новое состояние)
        """
        self.states: StatesGroup = state_factory(self.get_state_group_class(), state_base_name)
        self.on_success = on_success
        self.on_next = on_next

    def get_state_group_class(self) -> StatesGroup:
        return BaseComponentState

