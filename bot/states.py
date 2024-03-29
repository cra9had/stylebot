from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class SearchStates(StatesGroup):
    prompt = State()
    searching = State()


class ProfileParameters(StatesGroup):
    input_sex = State()
    input_age = State()
    input_size = State()
    input_city = State()


class ProfileMenuStates(StatesGroup):
    main_menu = State()


class AdjustSettings(StatesGroup):

    adjust_min_price = State()
    adjust_max_price = State()
