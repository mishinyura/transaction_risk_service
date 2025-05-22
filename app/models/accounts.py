from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base_model import BaseModel, BaseInit


class AccountModel(BaseInit):
    __tablename__ = 'accounts'

    account_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    middle_name: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    create_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
