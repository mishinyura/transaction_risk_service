from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine

from config import settings as app_settings


class DatabaseHelper:
    def __init__(
            self,
            url: str,
            echo: bool = False,
            echo_pool: bool = False,
            pool_size: int = 10,
            max_overflow: int = 20,
    ) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    async def dispose(self) -> None:
        """Закрывает все соединения в пуле движка."""
        await self._engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Предоставляет асинхронную сессию SQLAlchemy."""
        async_session = self._session_factory()
        try:
            yield async_session
        except Exception:
            await async_session.rollback()
            raise
        finally:
            await async_session.close()


db_helper = DatabaseHelper(
    url=app_settings.db.url,
    echo=app_settings.db.echo,
    echo_pool=app_settings.db.echo_pool,
    pool_size=app_settings.db.pool_size,
    max_overflow=app_settings.db.max_overflow,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with db_helper.get_session() as session:
        yield session
