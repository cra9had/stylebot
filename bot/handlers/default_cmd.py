from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.gpt import ChatGPT

chatGpt = ChatGPT()

r = Router()


@r.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        str(await chatGpt.get_search_queries("Привет!", user_sex="мужчина"))
    )
