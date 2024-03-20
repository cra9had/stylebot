import asyncio
import logging
import sys
from os import getenv

import databases
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.enums import ParseMode

TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()


async def main() -> None:
    db_url = (
        f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@"
        f"127.0.0.1:5432/{getenv('POSTGRES_DB')}"
    )
    database = databases.Database(db_url)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
