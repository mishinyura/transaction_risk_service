from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import SqlException
from app.models.transactions import TransactionModel
from app.schemas.transactions import TransactionSchema
from app.databases.base_crud import BaseCRUD


class TransactionCRUD(BaseCRUD):
    @classmethod
    async def get_transaction(cls, transaction_id: int, session: AsyncSession) -> TransactionSchema:
        result = await session.execute(select(TransactionModel).where(transaction_id == TransactionModel.id))
        transaction = result.scalar_one_or_none()
        return TransactionSchema.model_validate(transaction)

    @classmethod
    async def get_account_send_transactions(cls, account_id: str, session: AsyncSession) -> list[TransactionSchema] | list:
        result = await session.execute(select(TransactionModel).where(account_id == TransactionModel.sender_account_id))
        transactions = result.scalars().all()
        return [TransactionSchema.model_validate(transaction) for transaction in transactions]

    @classmethod
    async def get_account_received_transactions(cls, account_id: str, session: AsyncSession) -> list[TransactionSchema] | list:
        result = await session.execute(select(TransactionModel).where(account_id == TransactionModel.receiver_account_id))
        transactions = result.scalars().all()
        return [TransactionSchema.model_validate(transaction) for transaction in transactions]

    @classmethod
    async def get_transaction_devices(cls, transaction: TransactionSchema, start_date, session: AsyncSession) -> set:
        result = await session.execute(
            select(TransactionModel.device_user)
            .where(
                TransactionModel.sender_account_id == transaction.sender_account_id,
                TransactionModel.transaction_datetime >= start_date
            )
            .distinct()
        )
        recent_devices = {row[0] for row in result.all()}
        return recent_devices

    async def get_all(self, session: AsyncSession) -> list[TransactionSchema]:
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