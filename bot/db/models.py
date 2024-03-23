import asyncio
from typing import Optional
from sqlalchemy import ForeignKey, String, BigInteger, select
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from sqlalchemy.ext.asyncio import AsyncAttrs, async_session, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DB_URL = 'sqlite+aiosqlite:///:memory:'


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tgname: Mapped[Optional[str]]

    #body: Mapped["Body"] = relationship(back_populates="user")

    def __repr__(self):
        return f"{self.tg_id=} {self.tgname=}"


class Body(Base):
    __tablename__ = "bodies"
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sex: Mapped[str]
    age: Mapped[str]
    size: Mapped[str]

    #user: Mapped["User"] = relationship(back_populates="body")

    def __repr__(self):
        return f'{self.tg_id=} {self.sex=}, {self.age=}, {self.size=}'


if __name__ == '__main__':
    async def add_user(session, tg_id, tgname):
        try:
            user = User(tg_id=tg_id, tgname=tgname)
            session.add(user)
            await session.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False


    async def add_body(session, tg_id, sex, age, size):
        try:
            user = await session.execute(select(User).filter(User.tg_id == tg_id))
            user = user.scalar_one_or_none()
            if user:
                body = Body(tg_id=tg_id, sex=sex, age=age, size=size)
                body.user = user
                session.add(body)
                await session.commit()
                return True
            else:
                print("User not found")
                return False
        except Exception as e:
            print(f"Error adding body: {e}")
            return False


    async def main():
        engine = create_async_engine(url=DB_URL, future=True, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        db_pool = async_sessionmaker(engine, expire_on_commit=False)

        async with db_pool() as session:
            user_added = await add_user(session, tg_id=1, tgname="John")
            if user_added:
                print("User added successfully")
                body_added = await add_body(session, tg_id=1, sex="Male", age="30", size="Large")
                if body_added:
                    print("Body added successfully")


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
