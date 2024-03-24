from typing import List, Sequence

import sqlalchemy.exc
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import selectinload

from bot.db.models import User, Body, Geo


async def get_users(session: AsyncSession, tg_id: int | None = None) -> Sequence[User] | User | None:
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


async def get_locations(session: AsyncSession):
    request = await session.execute(select(Geo))

    return request.scalars().all()


async def add_body(session: AsyncSession, tg_id: int, sex: str, age: int, size: str):
    try:
        body_query = await session.execute(select(Body).filter(Body.tg_id == tg_id))
        body = body_query.scalar_one_or_none()
        if not body:
            user_query = await session.execute(select(User).filter(User.tg_id == tg_id))
            user = user_query.scalar_one_or_none()
            print("USER IN ADD_BODY:", user)

            if not user:
                raise RuntimeError(f"в add_body не был найден User с tg_id={tg_id}")

            body = Body(sex=sex, age=age, size=size)
            body.user = user
            session.add(body)
            await session.commit()
        else:
            print("Body's already there")

    except Exception as e:
        print(f"Error adding body: {e}")


async def add_geo(session: AsyncSession, tg_id: int, dest_id: int):
    try:
        location_query = await session.execute(select(Geo).filter(Geo.tg_id == tg_id))
        location = location_query.scalar_one_or_none()

        if not location:
            user_query = await session.execute(select(User).filter(User.tg_id == tg_id))
            user = user_query.scalar_one_or_none()
            print("USER IN ADD_GEO:", user)

            if not user:
                raise RuntimeError(f"в add_location не был найден User с tg_id={tg_id}")

            geo = Geo(tg_id=tg_id, wb_city_id=dest_id)
            geo.user = user
            session.add(geo)
            await session.commit()
        else:
            print("Body's already there")

    except Exception as e:
        print(f"Error adding body: {e}")
