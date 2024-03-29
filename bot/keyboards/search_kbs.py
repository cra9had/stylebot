from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.db.constants import DEFAULT_MAX_PRICE


def get_search_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="👍",
    )
    builder.button(
        text="👎",
    )

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_product_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="🔍Продолжить поиск",
    )

    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)


def get_price_kb(min_price: int | None = None, max_price: int | None = None):
    builder = InlineKeyboardBuilder()
    builder.button(text="Минимальная цена", callback_data="ignore_callback")
    builder.button(text="Максимальная цена", callback_data="ignore_callback")

    builder.button(text=f"{min_price} ₽", callback_data="change_min_price")

    if max_price != DEFAULT_MAX_PRICE:
        builder.button(text=f"{max_price} ₽", callback_data="change_max_price")
    else:
        builder.button(text=f"∞", callback_data="change_max_price")

    builder.button(text="Сбросить цены", callback_data="reset_price")

    builder.adjust(2, 2, 1)

    return builder.as_markup()
