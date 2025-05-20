from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Response
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.app.secret_key
COOKIE_NAME = settings.app.cookie_name
COOKIE_MAX_AGE_DAYS = settings.app.cookie_max_age_days
COOKIE_MAX_AGE_SECONDS = int(timedelta(days=COOKIE_MAX_AGE_DAYS).total_seconds())

serializer = URLSafeTimedSerializer(SECRET_KEY)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_session_cookie(response: Response, username: str) -> None:
    session_data = {"sub": username}
    session_id = serializer.dumps(session_data)
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_id,
        max_age=COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )


def get_username_from_session_cookie(session_id: str | None) -> str | None:
    if session_id is None:
        return None
    try:
        data = serializer.loads(session_id, max_age=COOKIE_MAX_AGE_SECONDS)
        return data.get("sub")
    except (SignatureExpired, BadTimeSignature):
        return None
    except Exception:
        return None


def delete_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )