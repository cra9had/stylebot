from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.db.models import Favourite
from bot.cbdata import FavouriteItemsFactory, PageNumFactory


def make_profile_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='🎯Подобрать образ', callback_data="start_search_clothes"
    )
    builder.button(
        text='⭐Избранное', callback_data='go_favourite_menu'
    )
    builder.button(
        text='🧢Профиль', callback_data='go_profile_menu'
    )
    builder.button(
        text='✅Пополнить баланс', callback_data='go_payment_menu'
    )

    builder.adjust(2)

    return builder.as_markup()


def make_profile_body_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Изменить параметры профиля', callback_data='re_enter_body_parameters'
    )
    builder.button(
        text='Вернуться назад', callback_data="go_back_profile_menu"
    )

    builder.adjust(2)

    return builder.as_markup()


def make_favourite_kb(favourites: list[Favourite], page: int, max_page: int):
    builder = InlineKeyboardBuilder()

    for favourite in favourites:
        builder.button(
            text=f'{favourite.wb_item_id}', callback_data=FavouriteItemsFactory(wb_item_id=favourite.wb_item_id)
        )

    builder.adjust(1)

    paginate_builder = InlineKeyboardBuilder()

    if page == 1:
        paginate_builder.button(text=" ", callback_data="ignore_pagination")
    else:
        paginate_builder.button(text="<-", callback_data=PageNumFactory(page_num=page))

    paginate_builder.button(text=f"{page}/{max_page}", callback_data="ignore_pagination")

    if page == max_page:
        paginate_builder.button(text=" ", callback_data="ignore_pagination")
    else:
        paginate_builder.button(text="->", callback_data=PageNumFactory(page_num=page))

    paginate_builder.adjust(3)

    builder.attach(paginate_builder)

    return builder.as_markup()
