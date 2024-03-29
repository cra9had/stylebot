from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.db.orm import get_users
from bot.middlewares.user_exists import UserExistsMiddleware
from bot.keyboards.profile_kbs import make_profile_kb
from services.gpt import ChatGPT

chatGpt = ChatGPT()

r = Router()

r.message.middleware(UserExistsMiddleware())


@r.message(Command(commands=['start', 'menu']))
async def start_cmd(message: Message, session: AsyncSession, state: FSMContext):

    user: User = await get_users(session, message.chat.id)

    if not user.body:
        message_text = 'Привет!\n\nЭто <b>бот подбора одежды с Wildberries</b> 🍇\n\nДавай определимся с твоими параметрами 📏:'
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Ввести размеры", callback_data='input_sizes')]]
        )
    else:
        message_text = f'☰ Меню бота подбора одежды с Wildberries 🍇\n'
        kb = make_profile_kb()

    await message.answer(text=message_text, reply_markup=kb)
