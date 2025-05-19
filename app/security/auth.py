import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings as app_config
from app.models.db_helper import get_db_session
from app.models.user import User as UserModel
from app.crud import user as user_crud
from app.schemas.token_schema import TokenPayload

# Логгер можно добавить, если он будет инициализирован
# from app.core.logger import app_logger # Если будет логгер

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Утилиты для паролей ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --- Утилиты для JWT ---
SECRET_KEY_BYTES: bytes = app_config.app.secret_key
ALGORITHM: str = app_config.app.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = app_config.app.access_token_expire_minutes
ACCESS_TOKEN_COOKIE_NAME: str = app_config.app.access_token_cookie_name
COOKIE_SECURE_FLAG: bool = app_config.app.cookie_secure_flag


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})  # JWT ожидает timestamp для exp

    if "sub" not in to_encode:
        # app_logger.error("Subject ('sub') claim is required for JWT creation")
        print("ERROR: Subject ('sub') claim is required for JWT creation")
        raise ValueError("Subject ('sub') claim is required for JWT")

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_BYTES.decode('utf-8'),
                             algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, SECRET_KEY_BYTES.decode('utf-8'), algorithms=[ALGORITHM])
        if "user_id" in payload and isinstance(payload["user_id"], str):
            try:
                payload["user_id"] = uuid.UUID(payload["user_id"])
            except ValueError:
                print(f"WARNING: Invalid user_id format in token: {payload['user_id']}")
                return None
        return TokenPayload(**payload)
    except JWTError as e:
        # app_logger.warning(f"JWT decoding error: {e}")
        print(f"WARNING: JWT decoding error: {e}")
        return None


# --- Аутентификация пользователя ---
async def authenticate_user(
        session: AsyncSession, username: str, password: str
) -> Optional[UserModel]:
    user = await user_crud.get_user_by_username(session, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# --- Зависимости FastAPI для получения текущего пользователя ---
async def get_token_from_cookie(
        access_token_value: Optional[str] = Cookie(None, alias=ACCESS_TOKEN_COOKIE_NAME)
) -> Optional[str]:
    if not access_token_value:
        return None
    return access_token_value


async def get_current_user(
        session: AsyncSession = Depends(get_db_session),
        token_value: Optional[str] = Depends(get_token_from_cookie)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials, token missing or invalid",
    )
    if token_value is None:
        raise credentials_exception

    token_data = decode_access_token(token_value)
    if token_data is None or token_data.sub is None:
        raise credentials_exception

    user = await user_crud.get_user_by_username(session, username=token_data.sub)
    if user is None:
        # app_logger.warning(f"User '{token_data.sub}' from token not found in DB.")
        print(f"WARNING: User '{token_data.sub}' from token not found in DB.")
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if not current_user.is_active:
        # app_logger.warning(f"User '{current_user.username}' is inactive.")
        print(f"WARNING: User '{current_user.username}' is inactive.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
        current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    if not current_user.is_superuser:
        # app_logger.warning(f"User '{current_user.username}' attempted superuser action without rights.")
        print(f"WARNING: User '{current_user.username}' attempted superuser action without rights.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
