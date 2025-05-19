from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_helper import db_manager
from app.models.user import User
from app.crud import user as crud_user
from app.security.core import get_username_from_session_cookie, COOKIE_NAME


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.get_session() as session:
        yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
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

    user = await crud_user.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь для сессии не найден",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user
