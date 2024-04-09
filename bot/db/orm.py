from datetime import datetime
from math import ceil
from typing import List, Sequence

import sqlalchemy.exc
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import selectinload

from bot.db.constants import Config, Subscriptions
from bot.db.models import User, Body, Geo, Favourite, SearchSettings, Transaction, Subscription
from wb.data import Product


async def get_users(session: AsyncSession, tg_id: int | None = None) -> Sequence[User] | User | None:
    """
    Gets users (optionally with filter of tg_id)

    :param tg_id: user tg_id
    :param session: SQLAlchemy DB session
    """

    if not tg_id:
        users_request = await session.execute(
            select(User).options(selectinload(User.body), selectinload(User.geo), selectinload(User.favourites),
                                 selectinload(User.settings), selectinload(User.subscriptions))
        )
        return users_request.scalars().all()
    else:
        users_request = await session.execute(
            select(User).where(User.tg_id == tg_id).options(selectinload(User.body), selectinload(User.geo),
                                                            selectinload(User.favourites), selectinload(User.settings),
                                                            selectinload(User.subscriptions))
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
    page_favourites = favourites[(page - 1) * Config.FAVOURITES_IN_PAGE.value: page * Config.FAVOURITES_IN_PAGE.value] \
        if page * Config.FAVOURITES_IN_PAGE.value < len(favourites) else favourites[
                                                                         (page - 1) * Config.FAVOURITES_IN_PAGE.value:]

    return page_favourites


async def get_max_page(session: AsyncSession, tg_id: int):
    favourites = await get_favourites(session, tg_id)
    max_page = ceil(len(favourites) / Config.FAVOURITES_IN_PAGE.value) or 1

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


async def get_settings(session: AsyncSession, tg_id: int | None = None) \
        -> Sequence[SearchSettings] | SearchSettings | None:
    if not tg_id:
        settings_request = await session.execute(
            select(SearchSettings).options(selectinload(SearchSettings.user))
        )
        return settings_request.scalars().all()
    else:
        settings_request = await session.execute(
            select(SearchSettings).where(SearchSettings.tg_id == tg_id).options(selectinload(SearchSettings.user))
        )
        return settings_request.scalar()


async def add_settings(session: AsyncSession, tg_id: int, min_price: int | None = None,
                       max_price: int | None = None, is_original: int = 0) -> None:
    try:
        settings_query = await session.execute(select(SearchSettings).filter(SearchSettings.tg_id == tg_id))
        settings = settings_query.scalar_one_or_none()

        if not settings:
            user_query = await session.execute(select(User).filter(User.tg_id == tg_id))
            user = user_query.scalar_one_or_none()

            if not user:
                raise RuntimeError(f"в add_settings не был найден User с tg_id={tg_id}")

            if min_price is not None and max_price is not None:
                settings = SearchSettings(tg_id=tg_id, min_price=min_price, max_price=max_price,
                                          is_original=is_original)
            elif min_price is None:
                settings = SearchSettings(tg_id=tg_id, max_price=max_price, is_original=is_original)
            elif max_price is None:
                settings = SearchSettings(tg_id=tg_id, min_price=min_price, is_original=is_original)
            else:
                settings = SearchSettings(tg_id=tg_id, is_original=is_original)

            settings.user = user
            session.add(settings)
            await session.commit()
        else:
            print("Settings're already there")
            if min_price is not None:
                settings.min_price = min_price
            if max_price is not None:
                settings.max_price = max_price
            settings.is_original = is_original
            await session.commit()

    except Exception as e:
        print(f"Error adding geo: {e}")


# create_transaction, confirm_transaction(trx_id), create_subscription

async def create_transaction(session: AsyncSession, tg_id: int, transaction_type: str) -> int:
    try:
        transaction = Transaction(tg_id=tg_id,
                                  date_creation=int(datetime.now().timestamp()),
                                  transaction_type=transaction_type)

        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)

        return transaction.id
    except Exception as e:
        print(f"Error creating transaction: {e}")


async def get_transactions(session: AsyncSession, user_id: int | None = None, trx_id: int | None = None):
    if user_id:
        trans_query = await session.execute(
            select(Transaction).filter(Transaction.tg_id == user_id).options(selectinload(Transaction.subscription))
        )
    elif trx_id:
        trans_query = await session.execute(
            select(Transaction).filter(Transaction.id == trx_id).options(selectinload(Transaction.subscription))
        )
        return trans_query.scalar_one_or_none()

    else:
        trans_query = await session.execute(
            select(Transaction).options(selectinload(Transaction.subscription))
        )

    return trans_query.scalars().all()


async def confirm_transaction(session: AsyncSession, trx_id: int, payment_date: int | datetime | None = None):
    trans = await get_transactions(session, trx_id=trx_id)

    if payment_date and isinstance(payment_date, datetime):
        payment_date = int(payment_date.timestamp())

    if not payment_date:
        payment_date = int(datetime.now().timestamp())

    trans.date_payment = payment_date

    await session.commit()


async def create_subscription(session: AsyncSession, trx_id: int, user_id: int):
    trx = await get_transactions(session, trx_id=trx_id)
    await confirm_transaction(session, trx_id)
    user = await get_users(session, user_id)

    sub = Subscription(
        transaction_id=trx_id)
    sub.transaction = trx
    sub.user = user

    session.add(sub)

    await session.commit()
    await session.refresh(sub)

    print(f"Subscription created with ID: {sub.id}")
    return sub.id


async def get_subscriptions(session: AsyncSession, tg_id: int | None = None):
    if tg_id:
        trans_query = await session.execute(
            select(Subscription).filter(Subscription.user_id == tg_id).options(selectinload(Subscription.transaction),
                                                                               selectinload(Subscription.user))
        )
    else:
        trans_query = await session.execute(
            select(Transaction).options(selectinload(Subscription.transaction),
                                        selectinload(Subscription.user))
        )

    return trans_query.scalars().all()


async def get_user_subscription(session: AsyncSession, user_id: int):
    subs = await get_subscriptions(session, user_id)
    max_sub_price = 0
    result_sub = None

    for sub in subs:
        tariff_type = sub.transaction.transaction_type
        subscription_details = getattr(Subscriptions, tariff_type).value
        if subscription_details['price'] > max_sub_price:
            result_sub = sub

    return result_sub
