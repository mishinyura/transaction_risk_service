from pydantic import BaseModel


class AccountSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str