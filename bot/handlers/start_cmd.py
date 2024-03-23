from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from services.gpt import ChatGPT
from bot.db.orm import get_users, add_body, check_body_for_tg_id
from bot.middlewares.user_exists import UserExistsMiddleware
from bot.states import Measures

chatGpt = ChatGPT()

r = Router()

r.message.middleware(UserExistsMiddleware())


@r.message(Command("start"))
async def start_cmd(message: Message, session_pool: async_sessionmaker, state: FSMContext):

    if not await check_body_for_tg_id(session_pool, message.from_user.id):
        message_text = '✋Добро пожаловать в бот подбора одежды с Wildberries\n📏🤏 Давай определимся с размерами:'
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Ввести размеры", callback_data='input_sizes')]]
        )
    else:
        message_text = f'✋Добро пожаловать в бот подбора одежды с Wildberries\n📏🤏:'
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главное меню", callback_data='go_menu')]]
        )

    await message.answer(
        text=message_text, reply_markup=kb
    )
