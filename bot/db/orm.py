from typing import List, Sequence

import sqlalchemy.exc
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import selectinload

from bot.db.models import User, Body


async def get_users(session: AsyncSession, tg_id: int | None = None) -> ScalarResult[User]:
    """
    Gets users (optionally with filter of tg_id)

    :param tg_id: user tg_id
    :param session: SQLAlchemy DB session
    """

    if not tg_id:
        users_request = await session.execute(
            select(User)
        )
        return users_request.scalars().all()
    else:
        users_request = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return users_request.scalar()




async def add_user(session: AsyncSession, tg_id: int, tgname: str = None):
    """
    Adds new user on patching the /start message
    """

    try:
        if tgname:
            user = User(tg_id=tg_id, tgname=tgname)
        else:
            user = User(tg_id=tg_id)
        session.add(user)
    except Exception as e:
        print(f"Error adding user: {e}")


async def get_bodies(session: AsyncSession):
    request = await session.execute(select(Body))

    return request.scalars().all()


async def add_body(session: AsyncSession, tg_id: int, sex: str, age: int, size: str):
    try:
        result = await session.execute(select(Body).filter(Body.tg_id == tg_id))
        body = result.scalar_one_or_none()
        if not body:
            body = Body(tg_id=tg_id, sex=sex, age=age, size=size)
            session.add(body)
            await session.commit()
        else:
            print("Body's already there")
    except Exception as e:
        print(f"Error adding body: {e}")
