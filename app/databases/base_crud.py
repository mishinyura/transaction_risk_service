from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any


class BaseCRUD(ABC):
    @abstractmethod
    async def get_all(self, session: AsyncSession) -> list[Any]: ...

    @abstractmethod
    async def add(self, obj: Any, session: AsyncSession) -> None: ...