from pydantic import BaseModel, ConfigDict


class AccountSchema(BaseModel):
    account_id: str
    first_name: str
    last_name: str
    middle_name: str
    risk: float

    model_config = ConfigDict(from_attributes=True)


class AccountRiskSchema(BaseModel):
    risk: float

    model_config = ConfigDict(from_attributes=True)
