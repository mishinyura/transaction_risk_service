import uuid as uuid_pkg
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id:                 Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                                              default=uuid_pkg.uuid4)
    username:           Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email:              Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=True)
    hashed_password:    Mapped[str] = mapped_column(String(256), nullable=False)
    full_name:          Mapped[str] = mapped_column(String(100), nullable=True)

    created_at:         Mapped[datetime] = mapped_column(
                            DateTime(timezone=True),
                            server_default=func.now(),
                            nullable=False
                        )

    updated_at:         Mapped[datetime] = mapped_column(
                            DateTime(timezone=True),
                            onupdate=func.now(),
                            nullable=True
                        )

    is_active:          Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser:       Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return (f"<User(id={self.id}, username='{self.username}', email='{self.email}', "
                f"is_active={self.is_active}, is_superuser={self.is_superuser})>")