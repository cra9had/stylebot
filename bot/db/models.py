import asyncio
from os import getenv
from typing import List
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tgname: Mapped[Optional[str]]

    body: Mapped["Body"] = relationship(back_populates="user")
    geo: Mapped["Geo"] = relationship(back_populates="user")
    favourites: Mapped[List["Favourite"]] = relationship(back_populates="user")
    settings: Mapped[List["SearchSettings"]] = relationship(back_populates="user")
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates='user')
    transactions: Mapped[List["Transaction"]] = relationship(back_populates='user')
    def __repr__(self):
        return f"{self.tg_id=} {self.tgname=}"


class Body(Base):
    __tablename__ = "bodies"
    tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id"), primary_key=True
    )
    sex: Mapped[str]
    age: Mapped[int]
    size: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="body")

    def get_sex_for_prompt(self) -> str:
        if self.sex == "male" and self.age <= 16:
            return "для парней"
        elif self.sex == "male":
            return "для мужчин"

        if self.sex == "female" and self.age <= 16:
            return "для девочек"
        else:
            return "для девушек"

    def __repr__(self):
        return f"{self.tg_id=} {self.sex=}, {self.age=}, {self.size=}"


class Geo(Base):
    __tablename__ = "user_location"

    tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id"), primary_key=True
    )
    wb_city_id: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="geo")

    def __repr__(self):
        return f"{self.tg_id=} {self.wb_city_id=}"


class Favourite(Base):
    __tablename__ = "user_favourites"

    wb_item_id: Mapped[int] = mapped_column(primary_key=True)
    item_name: Mapped[str] = mapped_column(nullable=False)
    photo_link: Mapped[str] = mapped_column(nullable=False)
    item_price: Mapped[int] = mapped_column(nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"))

    user: Mapped["User"] = relationship(back_populates="favourites")

    def __repr__(self):
        return f"{self.tg_id=} {self.wb_item_id=}"


class SearchSettings(Base):
    __tablename__ = "search_settings"

    tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id"), primary_key=True
    )
    min_price: Mapped[Optional[int]]
    max_price: Mapped[Optional[int]]
    is_original: Mapped[Optional[int]]

    user: Mapped[List["User"]] = relationship(back_populates="settings")

    def __repr__(self):
        return f"{self.min_price=} {self.max_price=}"

    def get_prices(self):
        return self.min_price, self.max_price


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_creation: Mapped[int]
    date_payment: Mapped[Optional[int]]
    transaction_type: Mapped[str]
    tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))

    user: Mapped["User"] = relationship(back_populates='transactions')
    subscription: Mapped["Subscription"] = relationship(back_populates='transaction')
    def __repr__(self):
        return f'{self.id=} {self.date_creation=} {self.transaction_type=}'


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey('transactions.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))

    transaction: Mapped["Transaction"] = relationship(back_populates='subscription')
    user: Mapped["User"] = relationship(back_populates='subscriptions')



DATABASE_URL = getenv("DB_URL")
engine = create_async_engine(DATABASE_URL)
async_pool = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_pool() as session:
        return session


async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_models())
