from aiogram.dispatcher.filters.state import State, StatesGroup

class GirlFormStates(StatesGroup):
    entered = State()

class GirlFormNameStates(StatesGroup):
    entered = State()

class GirlFormPriceStates(StatesGroup):
    entered = State()