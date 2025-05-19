import uuid
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    email: EmailStr | None = None
    full_name: str | None = None


class UserRead(UserBase):
    id: uuid.UUID
    email: EmailStr | None = None
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True