from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from bot.db.models import Body
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from services.gpt import ChatGPT
from bot.db.orm import get_users, add_body
from bot.middlewares.user_exists import UserExistsMiddleware
from bot.states import Measures

chatGpt = ChatGPT()

r = Router()

r.message.middleware(UserExistsMiddleware())


@r.message(Command("start"))
async def start_cmd(message: Message, session: AsyncSession, state: FSMContext):
    #if not await check_body_for_tg_id(session, message.from_user.id):
    #    await add_body(session, age=22, sex='F', size='L', tg_id=message.from_user.id)
    result = await session.execute(select(Body).filter(Body.tg_id == message.from_user.id))
    body = result.scalar_one_or_none()

    if not body:
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
