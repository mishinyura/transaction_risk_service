from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import UserModel
from app.schemas.users import UserCreate, UserRead
from app.core.security import get_password_hash
from app.databases.base_crud import BaseCRUD


class UserCRUD(BaseCRUD):
    async def get_user_by_username(self, db: AsyncSession, username: str) -> UserRead | None:
        print("USER:", UserModel.username)
        result = await db.execute(select(UserModel).where(UserModel.username == username))
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[Any]:
        result = await session.execute(select(UserModel))
        return result.scalars().all()

    async def add(self, db: AsyncSession, user_in: UserCreate) -> UserRead:
        hashed_password = get_password_hash(user_in.password)
        db_user = UserModel(
            username=user_in.username,
            hashed_password=hashed_password,
            email=user_in.email,
            full_name=user_in.full_name
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user


user_crud = UserCRUD()