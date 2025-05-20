from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.core.enums import TransactionType, TransactionStatus, DeviceUser


class TransactionSchema(BaseModel):
    id: int
    sender_account_id: str
    receiver_account_id: str
    transaction_amount: float
    transaction_type: TransactionType
    timestamp: datetime
    transaction_status: TransactionStatus
    fraud_flag: bool
    geolocation: str
    device_user: DeviceUser

    model_config = ConfigDict(from_attributes=True)


class TransactionCreateSchema(BaseModel):
    sender_account_id: str
    receiver_account_id: str
    transaction_amount: float
    transaction_type: TransactionType
    timestamp: datetime
    transaction_status: TransactionStatus
    fraud_flag: bool
    geolocation: str
    device_user: DeviceUser