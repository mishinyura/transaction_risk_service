import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Уникальное имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Адрес электронной почты")
    full_name: Optional[str] = Field(None, max_length=100, description="Полное имя пользователя")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Пароль пользователя (минимум 8 символов)")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Новый адрес электронной почты")
    full_name: Optional[str] = Field(None, max_length=100, description="Новое полное имя")
    is_active: Optional[bool] = Field(None, description="Статус активности пользователя")


class UserPublic(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
