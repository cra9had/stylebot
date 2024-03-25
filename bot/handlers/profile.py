from math import ceil

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Body
from bot.db.orm import get_bodies, get_favourites, get_page_favourites, get_max_page
from bot.keyboards.profile_kbs import make_profile_kb, make_profile_body_kb, make_favourite_kb
from bot.states import ProfileMenuStates
from bot.utils.remove_reply import remove_reply_keyboard
from bot.cbdata import PageNumFactory

from bot.db.constants import FAVOURITES_IN_PAGE

r = Router()


@r.callback_query(F.data == "go_profile_menu")
async def get_profile(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    await remove_reply_keyboard(bot, callback.message.chat.id)

    user_body: Body = await get_bodies(session, callback.message.chat.id)

    msg_text = \
        f"""
        Ваши параметры:
        Пол: {user_body.sex}
        Возраст: {user_body.age}
        Размер одежды: {user_body.size}
        """

    await callback.message.answer(msg_text, reply_markup=make_profile_body_kb())


@r.callback_query(F.data == 'go_back_profile_menu')
async def go_main_menu(callback: CallbackQuery):
    message_text = f'☰ Меню бота подбора одежды с Wildberries 🍇\n'

    await callback.message.answer(
        text=message_text, reply_markup=make_profile_kb()
    )


@r.callback_query(F.data == 'go_favourite_menu')
async def go_main_menu(callback: CallbackQuery, session: AsyncSession, state: FSMContext):

    page = 1
    max_page = await get_max_page(session, tg_id=callback.message.chat.id)
    await state.update_data(max_page=max_page)
    page_favourites = await get_page_favourites(session, page=page, tg_id=callback.message.chat.id)

    message_text = f'⭐Избранное артикулов с Wildberries 🍇'
    await callback.message.answer(
        text=message_text, reply_markup=make_favourite_kb(page_favourites, page, max_page)
    )


@r.callback_query(PageNumFactory.filter())
async def go_next_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext, callback_data: PageNumFactory):

    data = await state.get_data()
    max_page = data['max_page']

    page = callback_data.page_num
    page_favourites = await get_page_favourites(session, page=page, tg_id=callback.message.chat.id)
    await state.update_data(page=page)

    message_text = f'⭐Избранное артикулов с Wildberries 🍇'
    await callback.message.edit_reply_markup(
        text=message_text, reply_markup=make_favourite_kb(page_favourites, page, max_page)
    )


@r.callback_query(F.data.in_(['ignore_pagination']))
async def ignore_callback(callback: CallbackQuery):

    await callback.answer()