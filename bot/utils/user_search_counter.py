import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from redis.asyncio import Redis

from bot.handlers.payments import no_free_searches_left

FREE_SEARCHES_AMOUNT = int(os.getenv("FREE_SEARCHES_AMOUNT"))


def search_counter(fn):
    async def wrapper(message: Message, state: FSMContext, redis: Redis, **kwargs):
        await redis.incr(f"search_counter_user_{message.chat.id}")
        if (
            int(await redis.get(f"search_counter_user_{message.chat.id}"))
            <= FREE_SEARCHES_AMOUNT
        ):
            return await fn(message, state, redis)
        await no_free_searches_left(message)

    return wrapper
