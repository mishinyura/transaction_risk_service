import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.security import auth as auth_security
from app.models.db_helper import get_db_session
from app.schemas.user_schema import UserPublic, UserCreate
from app.models.user import User as UserModel
from app.crud import user as user_crud

# from app.core.logger import app_logger # Если будет логгер

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/token", response_model=UserPublic)
async def login_for_access_token(
        response: Response,  # Для установки cookie
        session: AsyncSession = Depends(get_db_session),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    # app_logger.info(f"Login attempt for user: {form_data.username}") # Если есть логгер
    print(f"INFO: Login attempt for user: {form_data.username}")
    user = await auth_security.authenticate_user(
        session, username=form_data.username, password=form_data.password
    )
    if not user:
        print(f"WARNING: Failed login for user: {form_data.username} - incorrect credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        print(f"WARNING: Failed login for inactive user: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires_delta = timedelta(minutes=auth_security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_security.create_access_token(
        data={"sub": user.username, "user_id": str(user.id)},
        expires_delta=access_token_expires_delta
    )

    response.set_cookie(
        key=auth_security.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,  # Защита от XSS
        max_age=int(access_token_expires_delta.total_seconds()),
        path="/",  # Cookie доступна для всего сайта
        secure=auth_security.COOKIE_SECURE_FLAG,  # True для HTTPS, False для HTTP
        samesite="lax"  # "lax" или "strict" для защиты от CSRF
    )
    print(f"INFO: User {user.username} logged in successfully. Cookie set.")
    return user


@router.post("/logout")
async def logout(response: Response):
    print("INFO: Logout attempt. Clearing cookie.")
    response.delete_cookie(
        key=auth_security.ACCESS_TOKEN_COOKIE_NAME,
        path="/",
        secure=auth_security.COOKIE_SECURE_FLAG,
        httponly=True,
        samesite="lax"
    )
    return {"message": "Successfully logged out"}


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_new_user(
        user_in: UserCreate,
        session: AsyncSession = Depends(get_db_session)
):
    print(f"INFO: Registration attempt for username: {user_in.username}")
    existing_user = await user_crud.get_user_by_username(session, username=user_in.username)
    if existing_user:
        print(f"WARNING: Registration failed: Username '{user_in.username}' already registered.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if user_in.email:
        existing_email = await user_crud.get_user_by_email(session, email=user_in.email)
        if existing_email:
            print(f"WARNING: Registration failed: Email '{user_in.email}' already registered.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    new_user = await user_crud.create_user(session=session, user_in=user_in)
    print(f"INFO: User '{new_user.username}' registered successfully with ID {new_user.id}.")
    return new_user


@router.get("/me", response_model=UserPublic)
async def read_users_me(
        current_user: UserModel = Depends(auth_security.get_current_active_user)
):
    print(f"DEBUG: User {current_user.username} accessed /me endpoint.")
    return current_user
