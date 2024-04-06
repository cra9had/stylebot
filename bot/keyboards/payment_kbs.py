from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Приобрести подписку",
        callback_data="get_subscription",  # TODO: change callback_data
    )
    return builder.as_markup()
