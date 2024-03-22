from typing import Any
from aiogram.filters.callback_data import CallbackData


class SizeChartFactory(CallbackData, prefix='sizes'):
    size: str


class SexPickFactory(CallbackData, prefix='sex'):
    gender: str


class BodyConfirmFactory(CallbackData, prefix='body'):
    size: str
    age: int
    sex: str