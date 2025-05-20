import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import SqlException
from app.models.transactions import TransactionModel
from app.schemas.transactions import TransactionSchema
from app.databases.base_crud import BaseCRUD


class TransactionCRUD(BaseCRUD):
    async def get_transaction(self, transaction_id: int, session: AsyncSession):
        result = await session.execute(select(TransactionModel).where(transaction_id == TransactionModel.id))
        transaction = result.scalar_one_or_none()
        return TransactionSchema.model_validate(transaction)

    async def get_all(self, session: AsyncSession) -> list[TransactionSchema] | list:
        result = await session.execute(select(TransactionModel))
        transactions = result.scalars().all()
        return [TransactionSchema.model_validate(transaction) for transaction in transactions]

    async def add(self, transaction: TransactionModel, session: AsyncSession) -> None:
        try:
            session.add(transaction)
            await session.commit()
        except SQLAlchemyError as exc:
            await session.rollback()
            raise SqlException(message=str(exc))


transaction_crud = TransactionCRUD()