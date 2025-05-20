from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseInit(DeclarativeBase):
    pass


class BaseModel:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
