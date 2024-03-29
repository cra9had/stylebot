import asyncio
from math import ceil

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from bot.cbdata import FavouriteItemsFactory
from bot.cbdata import PageNumFactory
from bot.db.constants import DEFAULT_MIN_PRICE, DEFAULT_MAX_PRICE
from bot.db.models import Body
from bot.db.orm import get_bodies, add_settings, get_settings
from bot.db.orm import get_favourites
from bot.db.orm import get_max_page
from bot.db.orm import get_page_favourites
from bot.keyboards.profile_kbs import make_favourite_kb
from bot.keyboards.profile_kbs import make_profile_body_kb
from bot.keyboards.profile_kbs import make_profile_kb
from bot.states import ProfileMenuStates, SearchStates, AdjustSettings
from bot.utils.remove_reply import remove_reply_keyboard

r = Router()


@r.callback_query(F.data == "go_profile_menu")
async def get_profile(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    await remove_reply_keyboard(bot, callback.message.chat.id)

    await callback.message.delete()

    user_body: Body = await get_bodies(session, callback.message.chat.id)

    msg_text = f"""
                Ваши параметры:
                Пол: {user_body.sex}
                Возраст: {user_body.age}
                Размер одежды: {user_body.size}
                """

    await callback.message.answer(msg_text, reply_markup=make_profile_body_kb())

    await callback.answer()


@r.callback_query(F.data == "go_back_profile_menu")
async def go_main_menu(callback: CallbackQuery):
    await callback.message.delete()
    message_text = f"☰ Меню бота подбора одежды с Wildberries 🍇\n"

    await callback.message.answer(text=message_text, reply_markup=make_profile_kb())


@r.message(F.text == 'Вернуться в меню', SearchStates.searching)
async def go_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await remove_reply_keyboard(message.bot, message.chat.id)

    message_text = f"☰ Меню бота подбора одежды с Wildberries 🍇\n"
    await message.answer(text=message_text, reply_markup=make_profile_kb())


@r.callback_query(F.data == "go_favourite_menu")
async def go_main_menu(
        callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    await callback.message.delete()

    data = await state.get_data()

    try:
        page = data["page"]
    except KeyError:
        page = 1

    max_page = await get_max_page(session, tg_id=callback.message.chat.id)
    await state.update_data(max_page=max_page)
    page_favourites = await get_page_favourites(
        session, page=page, tg_id=callback.message.chat.id
    )

    message_text = f"⭐Избранное артикулов с Wildberries 🍇"
    await callback.message.answer(
        text=message_text,
        reply_markup=make_favourite_kb(page_favourites, page, max_page),
    )


@r.callback_query(PageNumFactory.filter())
async def go_next_page(
        callback: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        callback_data: PageNumFactory,
):
    data = await state.get_data()
    max_page = data["max_page"]

    page = callback_data.page_num
    page_favourites = await get_page_favourites(
        session, page=page, tg_id=callback.message.chat.id
    )
    await state.update_data(page=page)

    message_text = f"⭐Избранное артикулов с Wildberries 🍇"
    await callback.message.edit_reply_markup(
        text=message_text,
        reply_markup=make_favourite_kb(page_favourites, page, max_page),
    )


@r.callback_query(FavouriteItemsFactory.filter())
async def get_favourite_item(
        callback: CallbackQuery, session: AsyncSession, callback_data: FavouriteItemsFactory
):
    await callback.message.delete()

    favourite_item = await get_favourites(session, wb_item_id=callback_data.wb_item_id)
    await callback.message.answer_photo(
        f"{favourite_item.photo_link}",
        caption=f"<b>{favourite_item.item_name}</b>\nЦена: {favourite_item.item_price} ₽\nАртикул: <code>{favourite_item.wb_item_id}</code>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Вернуться назад", callback_data="go_favourite_menu"
                    )
                ]
            ]
        ),
    )


@r.callback_query(F.data == "change_min_price")
async def change_min_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(AdjustSettings.adjust_min_price)
    del_msg = await callback.message.answer(
        "Введите значение минимальной цены (в рублях) для следующих образов одежды:"
    )
    await state.update_data(del_msg=del_msg.message_id)
    await callback.answer()


@r.callback_query(F.data == "change_max_price")
async def change_max_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(AdjustSettings.adjust_max_price)
    del_msg = await callback.message.answer(
        "Введите значение максимальной цены (в рублях) для следующих образов одежды:"
    )
    await state.update_data(del_msg=del_msg.message_id)
    await callback.answer()


@r.message(AdjustSettings.adjust_min_price)
async def set_min_price(message: Message, state: FSMContext, session: AsyncSession):
    new_min_price = message.text
    data = await state.get_data()
    del_msg_id = data["del_msg"]

    settings = await get_settings(session, message.chat.id)
    try:
        if settings.max_price > int(new_min_price):
            await message.bot.delete_message(message.chat.id, del_msg_id)
            await add_settings(session, message.chat.id, min_price=new_min_price)

            to_delete = await message.answer("Новое значение записано.")
            await asyncio.sleep(1)
            await to_delete.delete()
            await message.answer(
                "Теперь вы можете вернуться к поиску",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Вернуться к поиску",
                                callback_data="restart_search_clothes",
                            )
                        ]
                    ]
                ),
            )
    except ValueError:
        return


@r.message(AdjustSettings.adjust_max_price)
async def set_max_price(message: Message, state: FSMContext, session: AsyncSession):
    new_max_price = message.text
    data = await state.get_data()
    del_msg_id = data["del_msg"]

    settings = await get_settings(session, message.chat.id)
    try:
        if settings.min_price < int(new_max_price):
            await message.bot.delete_message(message.chat.id, del_msg_id)
            await add_settings(session, message.chat.id, max_price=new_max_price)

            to_delete = await message.answer("Новое значение записано.")
            await asyncio.sleep(1)
            await to_delete.delete()
            await message.answer(
                "Теперь вы можете вернуться к поиску",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Вернуться к поиску",
                                callback_data="restart_search_clothes",
                            )
                        ]
                    ]
                ),
            )
    except ValueError:
        return


@r.callback_query(F.data == "reset_price")
async def reset_price(callback: CallbackQuery, session: AsyncSession):
    await add_settings(
        session,
        callback.message.chat.id,
        min_price=DEFAULT_MIN_PRICE,
        max_price=DEFAULT_MAX_PRICE,
    )

    await callback.message.delete()
    await callback.message.answer(
        "Настройки цен сброшены.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Вернуться к поиску",
                        callback_data="restart_search_clothes",
                    )
                ]
            ]
        ),
    )
    await callback.answer()


@r.callback_query(F.data.in_(["ignore_pagination", "ignore_callback"]))
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()

