import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    username: str
    password: str
    email: EmailStr
    full_name: str


class UserRead(UserBase):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True