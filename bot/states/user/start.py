from aiogram.dispatcher.filters.state import State, StatesGroup


class MainMenuStates(StatesGroup):
    select_sex = State()