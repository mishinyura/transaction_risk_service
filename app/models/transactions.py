from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    Boolean,
    ForeignKey,
    Enum as Enalchemy
)
from sqlalchemy.orm import validates, Mapped, mapped_column

from app.core.enums import TransactionStatus, TransactionType, DeviceUser
from app.models.base_model import BaseModel, BaseInit


class TransactionModel(BaseModel, BaseInit):
    __tablename__ = 'transactions'

    sender_account_id: Mapped[str] = mapped_column(String, ForeignKey('accounts.account_id'), nullable=False)
    receiver_account_id: Mapped[str] = mapped_column(String, ForeignKey('accounts.account_id'), nullable=False)
    transaction_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(Enalchemy(TransactionType), nullable=False)
    transaction_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    transaction_status: Mapped[TransactionStatus] = mapped_column(Enalchemy(TransactionStatus), nullable=False)
    fraud_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    geolocation: Mapped[str] = mapped_column(String, nullable=False)
    device_user: Mapped[DeviceUser] = mapped_column(Enalchemy(DeviceUser), nullable=False)

    @validates('transaction_amount')
    def validate_transaction_amount(self, key, amount):
        if amount <= 0:
            raise ValueError('Сумма не может быть меньше или равной 0')
        return amount

    @validates('transaction_datetime')
    def validate_transaction_date(self, key, date):
        if date > datetime.now():
            raise ValueError('Неверная дата')
        return date