from fastapi import APIRouter, Depends, HTTPException, status, Response, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schema import UserCreate, UserRead
from app.services import auth_service
from app.security.dependencies import get_db, get_current_active_user
from app.security.core import create_session_cookie, delete_session_cookie
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    """
    user = await auth_service.register_new_user(db=db, user_in=user_in)
    return user


@router.post("/login")
async def login_for_session_cookie(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Вход для получения сессионной cookie. Имя пользователя и пароль должны быть отправлены как form data.
    """
    user = await auth_service.authenticate_user(db, username=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Cookie"},
        )
    create_session_cookie(response=response, username=user.username)
    return {"message": "Вход выполнен успешно"}


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user)
):
    """
    Выход и очистка сессионной cookie.
    """
    delete_session_cookie(response=response)
    return {"message": "Выход выполнен успешно"}


@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение данных текущего вошедшего пользователя.
    """
    return current_user
