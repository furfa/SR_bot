from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminPanelStates(StatesGroup):
    password = State()
    menu     = State()
    support_admin = State()
    support_answer = State()