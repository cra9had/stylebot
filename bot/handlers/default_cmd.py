from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from services.gpt import ChatGPT
from db.orm import get_users, add_user
chatGpt = ChatGPT()

r = Router()


@r.message(Command("start"))
async def start_cmd(message: Message, session: AsyncSession):
    users = await get_users(session)
    await message.answer(
        str(users)
    )
