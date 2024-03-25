from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Body
from bot.db.orm import get_bodies
from bot.keyboards.profile_kbs import make_profile_kb, make_profile_body_kb
from bot.states import ProfileMenuStates
from bot.utils.remove_reply import remove_reply_keyboard

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