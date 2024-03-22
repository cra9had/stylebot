from typing import List, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.db.models import User, Body


async def get_users(session: AsyncSession, tg_id: int | None = None) -> Sequence[User]:
    """
    Gets users (optionally with filter of tg_id)

    :param tg_id: user tg_id
    :param session: SQLAlchemy DB session
    """

    if not tg_id:
        users_request = await session.execute(
            select(User)
        )
    else:
        users_request = await session.execute(
            select(User).filter(User.tg_id == tg_id)
        )

    return users_request.scalars().all()


async def add_user(session: AsyncSession, tg_id: int, tgname: str = None):
    """
    Adds new user on patching the /start message
    """
    if tgname:
        user = User(tg_id=tg_id, tgname=tgname)
    else:
        user = User(tg_id=tg_id)
    session.add(user)
    # await session.commit()


async def get_body(session: AsyncSession, tg_id: int):
    result = await session.execute(select(User).filter(User.tg_id == tg_id).options(selectinload(User.body)))

    user = result.fetchone()

    if user:
        return user[0].body
    else:
        return None


async def add_body(session: AsyncSession, tg_id: int, sex: str, age: int, size: str):
    users = await get_users(session, tg_id)

    if not users:
        raise RuntimeError("BAD USER")

    user = users[0]

    body = Body(tg_id=tg_id, sex=sex, age=age, size=size)
    user.body = body
    session.add(body)
    #await session.commit()
