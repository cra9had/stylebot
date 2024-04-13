import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.constants import Subscriptions
from bot.db.orm import get_user_subscription
from bot.handlers.payments import no_free_searches_left

FREE_SEARCHES_AMOUNT = int(os.getenv("FREE_SEARCHES_AMOUNT"))


def search_counter(fn):
    async def wrapper(
        message: Message,
        state: FSMContext,
        redis: Redis,
        session: AsyncSession,
        **kwargs,
    ):
        is_subscribed = await get_user_subscription(session, message.chat.id)
        subscription_limit = FREE_SEARCHES_AMOUNT
        if is_subscribed:
            subscription_type = is_subscribed.transaction.transaction_type
            for subscription in Subscriptions:
                if subscription.name == subscription_type:
                    subscription_limit = subscription.value.get("likes_quantity")
        await redis.incr(f"search_counter_user_{message.chat.id}")
        if (
            int(await redis.get(f"search_counter_user_{message.chat.id}"))
            <= subscription_limit
        ):
            return await fn(message, state, redis, session)

        await no_free_searches_left(message, is_subscribed)

    return wrapper
