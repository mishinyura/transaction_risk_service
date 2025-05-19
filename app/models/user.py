import uuid as py_uuid
from datetime import datetime

from sqlalchemy import String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class User(Base):
    __tablename__ = "users"

    id:                 Mapped[py_uuid.UUID] = mapped_column(
                            UUID(as_uuid=True),
                            primary_key=True,
                            server_default=text("gen_random_uuid()"),
                            index=True,
                            nullable=False
                        )
    username:           Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password:    Mapped[str] = mapped_column(String, nullable=False)
    email:              Mapped[str | None] = mapped_column(String(120), unique=True, index=True, nullable=True)
    full_name:          Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at:         Mapped[datetime] = mapped_column(
                            server_default=func.now(),
                            nullable=False
                        )
    updated_at:         Mapped[datetime] = mapped_column(
                            server_default=func.now(),
                            onupdate=func.now(),
                            nullable=False
                        )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"