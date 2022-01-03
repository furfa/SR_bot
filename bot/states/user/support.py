from aiogram.dispatcher.filters.state import State, StatesGroup


class SupportStates(StatesGroup):
    client      = State()
    technical   = State()
    partnership_info = State()
    partnership = State()