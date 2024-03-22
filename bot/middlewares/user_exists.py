from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from sqlalchemy import select

from bot.db.models import User
from bot.db.orm import add_user


class UserExistsMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        from_user = data['event_from_user']
        session = data['session']

        db_query = await session.execute(select(User).filter_by(tg_id=from_user.id))
        user: User = db_query.scalar()

        if not user:
            username = from_user.username or None
            if not username:
                await add_user(session, tg_id=from_user.id)
            else:
                await add_user(session, tg_id=from_user.id, tgname=username)
            await session.commit()
            print(f"{from_user.username} добавлен в БД.")
        else:
            print(f"Добавлять не пришлось, {from_user.id} уже есть в БД.")
        return await handler(event, data)
