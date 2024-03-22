from typing import Optional
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from bot.db.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    tgname: Mapped[Optional[str]]

    body: Mapped["Body"] = relationship(back_populates="user")

    def __repr__(self):
        return f"{self.tg_id=} {self.tgname=}"


class Body(Base):
    __tablename__ = "body_parameters"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    sex: Mapped[str]
    age: Mapped[str]
    size: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="body")

    def __repr__(self):
        return f'{self.sex=}, {self.age=}, {self.size=}'