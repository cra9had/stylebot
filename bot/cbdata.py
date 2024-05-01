from typing import Any
from aiogram.filters.callback_data import CallbackData


class SizeChartFactory(CallbackData, prefix='sizes'):
    size: str


class SexPickFactory(CallbackData, prefix='sex'):
    gender: str


class ParamsConfirmFactory(CallbackData, prefix='params'):
    size: str
    age: int
    sex: str
    dest_id: int


class FavouriteItemsFactory(CallbackData, prefix='favourite'):
    wb_item_id: int


class PageNumFactory(CallbackData, prefix='pagination'):
    page_num: int


class SubTariffFactory(CallbackData, prefix='subscription'):
    name: str
    likes_quantity: int
    price: int


class CheckPaymentFactory(CallbackData, prefix='check_payment'):
    payment_id: str