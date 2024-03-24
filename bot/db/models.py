import asyncio
from os import getenv
from typing import Optional
from sqlalchemy import ForeignKey, String, BigInteger, select
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column, declarative_base

from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DB_URL = 'sqlite+aiosqlite:///:memory:'

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tgname: Mapped[Optional[str]]

    body: Mapped["Body"] = relationship(back_populates="user")

    def __repr__(self):
        return f"{self.tg_id=} {self.tgname=}"


class Body(Base):
    __tablename__ = "bodies"
    tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), primary_key=True)
    sex: Mapped[str]
    age: Mapped[int]
    size: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="body")

    def __repr__(self):
        return f'{self.tg_id=} {self.sex=}, {self.age=}, {self.size=}'


DATABASE_URL = getenv("DB_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
async_pool = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_pool() as session:
        return session


async def init_models():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_models())
