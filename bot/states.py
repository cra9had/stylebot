from aiogram.fsm.state import StatesGroup, State


class Measures(StatesGroup):
    input_sex = State()
    input_age = State()
    input_size = State()
