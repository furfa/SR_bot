from aiogram.dispatcher.filters.state import State, StatesGroup


class AccountStates(StatesGroup):
    enter_custom_amount = State()

    wait_screenshot = State()
