from typing import List, Sequence

import sqlalchemy.exc
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import selectinload

from bot.db.models import User, Body


async def get_users(session_pool: async_sessionmaker, tg_id: int | None = None) -> ScalarResult[User]:
    """
    Gets users (optionally with filter of tg_id)

    :param tg_id: user tg_id
    :param session: SQLAlchemy DB session
    """
    async with session_pool() as s:

        if not tg_id:
            users_request = await s.execute(
                select(User)
            )
        else:
            users_request = await s.execute(
                select(User).where(User.tg_id == tg_id)
            )

        return users_request.scalars().all()


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
        session.commit()
    except Exception as e:
        print(f"Error adding user: {e}")


async def get_bodies(session_pool: async_sessionmaker):
    async with session_pool() as s:
        request = await s.execute(select(Body))

        return request.scalars().all()


async def check_body_for_tg_id(session_pool: async_sessionmaker, tg_id):
    try:
        async with session_pool() as s:
            result = await s.execute(select(Body).filter(Body.tg_id == tg_id))
            body = result.scalar_one_or_none()
            if body:
                return True
            return False
    except Exception as e:
        print(f"Error checking for tg_id in Body: {e}")
        return False


async def add_body(session, tg_id, sex, age, size):
    try:
        async with session() as s:
            user = await s.execute(select(User).filter(User.tg_id == tg_id))
            user = user.scalar_one_or_none()
            if user:
                body = Body(tg_id=tg_id, sex=sex, age=age, size=size)
                body.user = user
                s.add(body)
            else:
                print("User not found")
    except Exception as e:
        print(f"Error adding body: {e}")
