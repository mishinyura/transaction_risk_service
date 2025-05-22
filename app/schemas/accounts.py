from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AccountSchema(BaseModel):
    account_id: str
    first_name: str
    last_name: str
    middle_name: str
    score: float
    create_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountRiskSchema(BaseModel):
    score: float

    model_config = ConfigDict(from_attributes=True)
