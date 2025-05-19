from fastapi import APIRouter, Depends
from typing import List

from app.models.user import User as UserModel
from app.security.auth import get_current_active_user, get_current_active_superuser, get_db_session
from app.schemas.user_schema import UserPublic

router = APIRouter(
    prefix="/protected",
    tags=["Protected Data"],
    dependencies=[Depends(get_current_active_user)]
)


@router.get("/data", response_model=dict)
async def get_protected_data(current_user: UserModel = Depends()): # Зависимость уже применена на уровне роутера
    return {"message": f"Hello {current_user.username}, this is protected data!"}


@router.get("/admin/data", response_model=dict)
async def get_admin_data(
    # Зависимость для суперпользователя применяется дополнительно к этой ручке
    current_superuser: UserModel = Depends(get_current_active_superuser)
):
    return {"message": f"Hello Admin {current_superuser.username}, this is super-secret admin data!"}


# Пример, если бы мы возвращали список пользователей (только для админа)
@router.get("/users", response_model=List[UserPublic], dependencies=[Depends(get_current_active_superuser)])
async def read_all_users(
    session=Depends(get_db_session),
    skip: int = 0,
    limit: int = 10
):
    from app.crud import user as user_crud
    users = await user_crud.get_users(session, skip=skip, limit=limit)
    return users
