from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.crud import user as crud_user
from app.schemas.user_schema import UserCreate
from app.models.user import User
from app.security.core import verify_password


async def register_new_user(db: AsyncSession, user_in: UserCreate) -> User:
    db_user = await crud_user.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже зарегистрировано"
        )
    return await crud_user.create_user(db=db, user_in=user_in)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    user = await crud_user.get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
