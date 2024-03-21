from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User


async def get_users(session: AsyncSession) -> List[User]:
    """
    Gets users, that've already pressed /start once

    :param session: SQLAlchemy DB session
    """

    users_request = await session.execute(
        select(User)
    )

    return users_request.scalars().all()


async def add_user(session: AsyncSession, tgname: str):
    """
    Adds new user on patching the /start message
    """
    user = User(tgname=tgname)
    session.add(user)
    await session.commit()
