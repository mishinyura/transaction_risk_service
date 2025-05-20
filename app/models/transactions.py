from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Enum as Enalchemy
)
from sqlalchemy.orm import validates

from app.core.enums import TransactionStatus, TransactionType, DeviceUser
from app.models.base_model import BaseModel, BaseInit


class TransactionModel(BaseModel, BaseInit):
    __tablename__ = 'transactions'

    sender_account_id = Column(String, ForeignKey('accounts.account_id'), nullable=False)
    receiver_account_id = Column(String, ForeignKey('accounts.account_id'), nullable=False)
    transaction_amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(Enalchemy(TransactionType), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    transaction_status = Column(Enalchemy(TransactionStatus), nullable=False)
    geolocation = Column(String, nullable=False)
    device_user = Column(Enalchemy(DeviceUser), nullable=False)

    @validates('transaction_amount')
    def validate_transaction_amount(self, key, amount):
        if amount <= 0:
            raise ValueError('Сумма не может быть меньше или равной 0')

    @validates('timestamp')
    def validate_timestamp(self, key, date):
        if date > datetime.now():
            raise ValueError('Неверная дата')