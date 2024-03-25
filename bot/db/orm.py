from math import ceil
from typing import List, Sequence

import sqlalchemy.exc
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import selectinload

from bot.db.constants import FAVOURITES_IN_PAGE
from bot.db.models import User, Body, Geo, Favourite
from wb.data import Product


async def get_users(session: AsyncSession, tg_id: int | None = None) -> Sequence[User] | User | None:
    """
    Gets users (optionally with filter of tg_id)

    :param tg_id: user tg_id
    :param session: SQLAlchemy DB session
    """

    if not tg_id:
        users_request = await session.execute(
            select(User).options(selectinload(User.body), selectinload(User.geo))
        )
        return users_request.scalars().all()
    else:
        users_request = await session.execute(
            select(User).where(User.tg_id == tg_id).options(selectinload(User.body), selectinload(User.geo))
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


async def get_bodies(session: AsyncSession, tg_id: int | None):
    if not tg_id:
        bodies_request = await session.execute(
            select(Body).options(selectinload(Body.user))
        )
        return bodies_request.scalars().all()
    else:
        bodies_request = await session.execute(
            select(Body).where(Body.tg_id == tg_id).options(selectinload(Body.user))
        )

        return bodies_request.scalar()


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

            if not user:
                raise RuntimeError(f"в add_body не был найден User с tg_id={tg_id}")

            body = Body(sex=sex, age=age, size=size)
            body.user = user
            session.add(body)
            await session.commit()
        else:
            print("Body's already there")
            body.sex = sex
            body.age = age
            body.size = size
            await session.commit()

    except Exception as e:
        print(f"Error adding body: {e}")


async def add_geo(session: AsyncSession, tg_id: int, dest_id: int) -> None:
    try:
        location_query = await session.execute(select(Geo).filter(Geo.tg_id == tg_id))
        location = location_query.scalar_one_or_none()

        if not location:
            user_query = await session.execute(select(User).filter(User.tg_id == tg_id))
            user = user_query.scalar_one_or_none()

            if not user:
                raise RuntimeError(f"в add_location не был найден User с tg_id={tg_id}")

            geo = Geo(tg_id=tg_id, wb_city_id=dest_id)
            geo.user = user
            session.add(geo)
            await session.commit()
        else:
            print("Geo's already there")
            location.wb_city_id = dest_id
            await session.commit()

    except Exception as e:
        print(f"Error adding geo: {e}")


async def get_user_profile_data(session: AsyncSession, tg_id: int):
    user_query = await session.execute(
        select(User).filter_by(tg_id=tg_id).options(
            selectinload(User.body),
            selectinload(User.geo)
        )
    )

    user = user_query.scalar_one_or_none()

    if user:
        return {
            'user_tg': user.tg_id,
            'body': {
                'sex': user.body.sex,
                'age': user.body.age,
                'size': user.body.size
            },
            'geo': {
                'wb_city_id': user.geo.wb_city_id
            }
        }
    else:
        return None


async def get_favourites(session: AsyncSession, tg_id: int | None = None, wb_item_id: int | None = None):
    if tg_id:
        user_query = await session.execute(
            select(User).filter_by(tg_id=tg_id).options(
                selectinload(User.favourites))
        )

        user = user_query.scalar_one_or_none()
        return user.favourites

    elif wb_item_id:
        favourite_request = await session.execute(
            select(Favourite).where(Favourite.wb_item_id == wb_item_id).options(selectinload(Favourite.user))
        )

        return favourite_request.scalar_one_or_none()


async def get_page_favourites(session: AsyncSession, tg_id: int, page: int):
    favourites = await get_favourites(session, tg_id)
    page_favourites = favourites[(page - 1) * FAVOURITES_IN_PAGE: page * FAVOURITES_IN_PAGE] \
        if page * FAVOURITES_IN_PAGE < len(favourites) else favourites[(page - 1) * FAVOURITES_IN_PAGE:]

    return page_favourites


async def get_max_page(session: AsyncSession, tg_id: int):
    favourites = await get_favourites(session, tg_id)
    max_page = ceil(len(favourites) / FAVOURITES_IN_PAGE) or 1

    return max_page


async def add_favourite_item(session: AsyncSession,
                             tg_id: int,
                             product: Product) -> None:
    try:
        favourite_query = await session.execute(select(Favourite).filter(Favourite.wb_item_id == product.id))
        favourite = favourite_query.scalar_one_or_none()

        if not favourite:
            user_query = await session.execute(select(User).filter(User.tg_id == tg_id))
            user = user_query.scalar_one_or_none()

            if not user:
                raise RuntimeError(f"в add_favourite_item не был найден User с tg_id={tg_id}")

            wb_item_id = product.id
            item_name = product.name
            photo_link = product.image_url
            item_price = product.price

            favourite = Favourite(tg_id=tg_id,
                                  wb_item_id=wb_item_id,
                                  item_name=item_name,
                                  photo_link=photo_link,
                                  item_price=item_price)
            favourite.user = user
            session.add(favourite)
            await session.commit()
        else:
            print("Favourite's already there")
            await session.commit()

    except Exception as e:
        print(f"Error adding favourite item: {e}")
