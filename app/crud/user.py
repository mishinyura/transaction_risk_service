import uuid
from typing import Optional, List, Sequence  # Sequence для .scalars().all()
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate  # Добавил UserUpdate
from app.security.auth_security import get_password_hash


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    result = await session.get(User, user_id)
    return result


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    stmt = select(User).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    hashed_password_val = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password_val,
        full_name=user_in.full_name
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user(session: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    await session.commit()
    await session.refresh(db_user)
    return db_user


async def delete_user(session: AsyncSession, db_user: User) -> None:
    await session.delete(db_user)
    await session.commit()
