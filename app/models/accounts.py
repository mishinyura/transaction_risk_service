from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel, BaseInit


class AccountModel(BaseInit):
    __tablename__ = 'accounts'

    account_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    middle_name: Mapped[str] = mapped_column(String, nullable=False)
    risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)