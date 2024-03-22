from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class SearchStates(StatesGroup):
    prompt = State()
    searching = State()


class Measures(StatesGroup):
    input_sex = State()
    input_age = State()
    input_size = State()
