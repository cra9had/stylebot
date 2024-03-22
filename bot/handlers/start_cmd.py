from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from services.gpt import ChatGPT
from bot.db.orm import get_users, get_body
from bot.middlewares.user_exists import UserExistsMiddleware
from bot.states import Measures

chatGpt = ChatGPT()

r = Router()

r.message.middleware(UserExistsMiddleware())

@r.message(Command("start"))
async def start_cmd(message: Message, session: AsyncSession, state: FSMContext):

    user_body = await get_body(session, message.from_user.id)

    if not user_body:
        message_text = '✋Добро пожаловать в бот подбора одежды с Wildberries\n📏🤏 Давай определимся с размерами:'
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Ввести размеры", callback_data='input_sizes')]]
        )
    else:
        message_text = f'✋Добро пожаловать в бот подбора одежды с Wildberries\n📏🤏 Твои размеры:\n{user_body}:'
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главное меню", callback_data='go_menu')]]
        )

    await message.answer(
        text=message_text, reply_markup=kb
    )
