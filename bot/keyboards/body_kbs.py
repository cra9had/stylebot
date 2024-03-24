from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.cbdata import SizeChartFactory, SexPickFactory, ParamsConfirmFactory


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


def make_city_choice_kb():
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(text='Отправить геолокацию', request_location=True)
    )
    builder.add(
        KeyboardButton(text='Не отправлять')
    )

    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)


def make_params_sum_kb(sex: str, age: int, size: str, dest_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='🔄 Заполнить заново', callback_data='re_enter_body_parameters'
    )
    builder.button(
        text='✅ Подтвердить', callback_data=ParamsConfirmFactory(age=age, size=size, sex=sex, dest_id=dest_id)
    )

    return builder.as_markup()