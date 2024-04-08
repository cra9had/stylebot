from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from sqlalchemy import select

from bot.db.models import User, get_session
from bot.db.orm import add_user, add_settings
from bot.db.constants import Config


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

            await add_settings(session, tg_id=from_user.id, min_price=Config.DEFAULT_MIN_PRICE.value, max_price=Config.DEFAULT_MAX_PRICE.value)
            print(f"{from_user.username} добавлен в БД.")

        else:
            print(f"Добавлять не пришлось, {from_user.id} уже есть в БД.")

        return await handler(event, data)
