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
        text="Предыдущая комбинация",
    )
    builder.button(
        text="Следующая комбинация",
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


def return_to_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Вернуться в меню", callback_data='go_back_profile_menu'
    )
    return builder.as_markup()


def start_search_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='🔍Поиск', callback_data='start_search_clothes'
    )

    return builder.as_markup()
