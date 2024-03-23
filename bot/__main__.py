import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from bot.db.models import async_pool
from bot.handlers.callbacks import r as callbacks_router
from bot.handlers.search import router as search_router
from bot.handlers.start_cmd import r as start_router
from bot.middlewares.db import DbSessionMiddleware

TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()


async def main() -> None:
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    dp.include_routers(start_router, callbacks_router, search_router)

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
