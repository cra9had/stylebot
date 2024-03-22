import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from bot.db.models import Base
from bot.handlers.start_cmd import r as start_router
from bot.handlers.callbacks import r as callbacks_router
from bot.middlewares.db import DbSessionMiddleware

TOKEN = getenv("BOT_TOKEN")
DB_URL = getenv("DB_URL")
dp = Dispatcher()

async def main() -> None:

    engine = create_async_engine(url=DB_URL, future=True, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    db_pool = async_sessionmaker(engine, expire_on_commit=False)

    dp.update.middleware(DbSessionMiddleware(session_pool=db_pool))

    dp.include_routers(start_router,
                       callbacks_router)

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
