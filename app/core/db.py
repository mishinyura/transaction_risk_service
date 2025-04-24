from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.models.base_model import BaseInit
from app.models import transactions, users, accounts

from config import settings

engine = create_async_engine(
    url=settings.db.get_url,
    echo=True
)

session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session():
    async with session_maker as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseInit.metadata.drop_all)
        await conn.run_sync(BaseInit.metadata.create_all)
