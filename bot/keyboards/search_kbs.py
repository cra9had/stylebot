from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


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
