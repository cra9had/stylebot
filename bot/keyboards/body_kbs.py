from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import SizeChartFactory, SexPickFactory


def make_sizes_kb():
    builder = InlineKeyboardBuilder()

    btn_texts = ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', '6XL', '7XL', '8XL', '9XL']
    for btn_text in btn_texts:
        builder.button(
            text=btn_text, callback_data=SizeChartFactory(size=btn_text)
        )

    builder.adjust(4)

    return builder.as_markup()


def make_sex_kb():
    builder = InlineKeyboardBuilder()

    # to copy paste -> 👩
    btn_texts = ['🧔🏻 Мужчина', '☕ Девушка']

    builder.button(
        text='🧔🏻 Мужчина', callback_data=SexPickFactory(gender='male')
    )
    builder.button(
        text='☕ Девушка', callback_data=SexPickFactory(gender='female')
    )

    builder.adjust(2)

    return builder.as_markup()


def make_body_again():
    builder = InlineKeyboardBuilder()

    builder.button(
        text='🔄 Заполнить заново', callback_data='re_enter_body_parameters'
    )

    return builder.as_markup()