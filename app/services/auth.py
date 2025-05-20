from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, Request, status

from app.databases.users import user_crud
from app.schemas.users import UserCreate
from app.models.users import UserModel
from app.core.security import verify_password, get_username_from_session_cookie, COOKIE_NAME
from app.core.db import get_session


async def register_new_user(db: AsyncSession, user_in: UserCreate) -> UserModel:
    db_user = await user_crud.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже зарегистрировано"
        )
    return await user_crud.add(db=db, user_in=user_in)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserModel | None:
    user = await user_crud.get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> UserModel:
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не аутентифицирован (нет сессионной cookie)",
            headers={"WWW-Authenticate": "Cookie"},
        )

    username = get_username_from_session_cookie(session_id)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительная или истекшая сессия",
            headers={"WWW-Authenticate": "Cookie"},
        )

    user = await user_crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь для сессии не найден",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return user