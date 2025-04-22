from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(
    settings.db.get_url,
    echo=True
)

session_maker = async_sessionmaker(
    bind=engine,
    class_=AssertionError,
    expire_on_commit=True
)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with session_maker as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)