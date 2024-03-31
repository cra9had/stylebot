from typing import List

from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.db.constants import DEFAULT_MAX_PRICE
from wb.data import Product


def get_search_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="<",
    )
    builder.button(
        text=">",
    )
    builder.button(
        text="Показать артикулы",
    )
    builder.button(
        text="Закрепить элемент",
    )
    builder.button(text="Вернуться в меню")
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_pin_keyboard(
    products: List[Product], pinned_products_id: List[int]
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    print(products, pinned_products_id)
    for i, product in enumerate(products):
        builder.button(
            text=f"{i + 1} {'✅' if product.id in pinned_products_id else '❌'}",
            callback_data=f"pin-product/{product.id}",
        )
    builder.button(text="Назад", callback_data="back_to_search")
    builder.adjust(2)

    return builder.as_markup()


def get_product_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="🔍Продолжить поиск",
    )

    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)


def return_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Вернуться в меню", callback_data="go_back_profile_menu")
    return builder.as_markup()


def start_search_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍Поиск", callback_data="start_search_clothes")

    return builder.as_markup()
