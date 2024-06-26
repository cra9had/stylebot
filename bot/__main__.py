import asyncio
import logging
import sys
from os import getenv

import aiocron
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis
import yookassa

from bot.handlers.payments import router as payments_router
from bot.handlers.profile import r as profile_router
from bot.handlers.registration import r as callbacks_router
from bot.handlers.search import router as search_router
from bot.handlers.start import r as start_router
from bot.middlewares.db import DbSessionMiddleware

TOKEN = getenv("BOT_TOKEN")
redis_client = Redis.from_url("redis://redis:6379/1")
dp = Dispatcher(storage=RedisStorage(redis=redis_client))


async def reset_redis_counter():
    async for key in redis_client.scan_iter("search_counter_user_*"):
        await redis_client.delete(key)


async def main() -> None:
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())
    dp.pre_checkout_query.middleware(DbSessionMiddleware())

    dp.include_routers(
        start_router, callbacks_router, search_router, profile_router, payments_router
    )
    t = aiocron.crontab("0 0 * * *", func=reset_redis_counter)

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    await dp.start_polling(bot, redis=redis_client, yookassa=yookassa.Configuration)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
