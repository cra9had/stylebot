from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import SubTariffFactory
from bot.db.constants import Subscriptions


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Приобрести подписку",
        callback_data="go_buy_menu",
    )
    return builder.as_markup()


def get_payment_main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒Купить подписку", callback_data="go_buy_menu")
    builder.button(text="Вернуться назад", callback_data="go_back_profile_menu")
    builder.adjust(2)

    return builder.as_markup()


def get_tariffs_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🙂🕯 300 образов в день",
        callback_data=SubTariffFactory(**Subscriptions.light.value),
    )
    builder.button(
        text="😊💡500 образов в день",
        callback_data=SubTariffFactory(**Subscriptions.medium.value),
    )
    builder.button(
        text="🤩🔥1000 образов в день",
        callback_data=SubTariffFactory(**Subscriptions.rare.value),
    )
    builder.button(
        text="🌈💥Безлимит",
        callback_data=SubTariffFactory(**Subscriptions.unlimited.value),
    )

    builder.button(text="Вернуться назад", callback_data="go_payment_menu")

    builder.adjust(1)

    return builder.as_markup()


def get_one_tarif_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Купить подписку", callback_data="buy_sub_menu")

    builder.button(text="Вернуться назад", callback_data="go_buy_menu")

    builder.adjust(1)

    return builder.as_markup()
