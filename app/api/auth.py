from fastapi import APIRouter, Depends, HTTPException, status, Response, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserCreate, UserRead
from app.services.auth import register_new_user, authenticate_user, get_current_user
from app.core.db import get_session
from app.core.security import create_session_cookie, delete_session_cookie
from app.models.users import UserModel

auth_router = APIRouter(tags=["auth"])


@auth_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Регистрация нового пользователя.
    """
    new_user = await register_new_user(db=db, user_in=user)
    return new_user


@auth_router.post("/login")
async def login_for_session_cookie(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_session)
):
    """
    Вход для получения сессионной cookie. Имя пользователя и пароль должны быть отправлены как form data.
    """
    user = await authenticate_user(db, username=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Cookie"},
        )
    create_session_cookie(response=response, username=user.username)
    return {"message": "Вход выполнен успешно"}


@auth_router.post("/logout")
async def logout(
    response: Response,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Выход и очистка сессионной cookie.
    """
    delete_session_cookie(response=response)
    return {"message": "Выход выполнен успешно"}


@auth_router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Получение данных текущего вошедшего пользователя.
    """
    return current_user