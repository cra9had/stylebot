from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_profile_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='🎯Подобрать образ', callback_data="start_search_clothes"
    )
    builder.button(
        text='🧢Профиль', callback_data='go_profile_menu'
    )
    builder.button(
        text='✅Пополнить баланс', callback_data='go_payment_menu'
    )

    builder.adjust(2)

    return builder.as_markup()
