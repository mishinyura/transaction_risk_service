from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserRead
from app.security.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/protected", tags=["Защищенные"])


@router.get("/data", response_model=UserRead)
async def get_protected_data(current_user: User = Depends(get_current_active_user)):
    """
    Пример защищенного маршрута. Доступ только для аутентифицированных пользователей.
    Возвращает данные текущего пользователя.
    """
    return current_user


@router.get("/message")
async def get_protected_message(current_user: User = Depends(get_current_active_user)):
    """
    Еще один пример защищенного маршрута.
    """
    return {"message": f"Привет {current_user.username}, вы получаете доступ к защищенному контенту!"}