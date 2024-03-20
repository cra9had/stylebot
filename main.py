import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.enums import ParseMode

TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
