import asyncio
from datetime import datetime
from os import getenv

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload, sessionmaker

from bot.db.models import User, Subscription, get_session, init_models
from bot.db.orm import get_users, SUBSCRIPTION_VITALITY


async def check_users_subscriptions(session: AsyncSession):
    users = await get_users(session)
    for user in users:
        print(f"Проверка на подписку у tg_id={user.tg_id}")
        await check_user_subscriptions(session, user.tg_id)


async def check_user_subscriptions(session: AsyncSession, tg_id: int):
    result = await session.execute(
        select(User)
        .where(User.tg_id == tg_id)
        .options(selectinload(User.subscriptions).selectinload(Subscription.transaction))
    )

    user = result.scalars().first()

    if not user:
        raise RuntimeError(f"No such a user with tg_id={tg_id} in check_user_subscriptions")

    now_timestamp = int(datetime.now().timestamp())
    expired_subscriptions = []

    for subscription in user.subscriptions:
        if subscription.transaction and subscription.transaction.date_payment:
            if subscription.transaction.date_payment < now_timestamp - SUBSCRIPTION_VITALITY:
                expired_subscriptions.append(subscription)

    for subscription in expired_subscriptions:
        print(f"Подписка {subscription.id} просрочена для пользователя {tg_id}")
        await session.delete(subscription)

    await session.commit()


DATABASE_URL = getenv("DB_URL")
engine = create_async_engine(DATABASE_URL)
async_pool = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def main():
    session = await get_session()
    await check_users_subscriptions(session)

    print("Session created successfully, add your queries here.")


if __name__ == "__main__":
    asyncio.run(main())
