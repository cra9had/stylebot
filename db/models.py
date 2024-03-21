from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tgname: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"{self.tgname=}"