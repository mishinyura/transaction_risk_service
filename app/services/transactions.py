from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException, SqlException
from app.models.transactions import TransactionModel
from app.databases.transactions import transaction_crud
from app.schemas.transactions import TransactionCreateSchema, TransactionSchema


class TransactionService:
    def __init__(self):
        self.crud = transaction_crud

    async def get_all_transactions(self, session: AsyncSession) -> list[TransactionSchema]:
        transactions = await self.crud.get_all(session=session)
        return transactions

    async def get_transaction_by_transaction_id(
        self, transaction_id: str, session: AsyncSession
    ) -> TransactionSchema | None:
        transaction = await self.crud.get_transaction(
            transaction_id=transaction_id, session=session
        )
        return transaction

    async def get_account_send_transactions(
            self, account_id: str, session: AsyncSession,
    ) -> list[TransactionSchema] | list:
        transactions = await self.crud.get_account_send_transactions(
            account_id=account_id,
            session=session,
        )
        return transactions

    async def get_account_received_transactions(
            self, account_id: str, session: AsyncSession,
    ) -> list[TransactionSchema] | list:
        transactions = await self.crud.get_account_received_transactions(
            account_id=account_id,
            session=session,
        )
        return transactions

    async def create_transaction(
            self, transaction_data: TransactionCreateSchema, session: AsyncSession
    ) -> None:
        transaction = TransactionModel(
            sender_account_id=transaction_data.sender_account_id,
            receiver_account_id=transaction_data.receiver_account_id,
            transaction_amount=transaction_data.transaction_amount,
            transaction_type=transaction_data.transaction_type,
            timestamp=transaction_data.timestamp,
            transaction_status=transaction_data.transaction_status,
            fraud_flag=transaction_data.fraud_flag,
            geolocation=transaction_data.geolocation,
            device_user=transaction_data.device_user
        )
        try:
            await self.crud.add(transaction=transaction, session=session)
        except SqlException as exc:
            raise DuplicateException(message=str(exc))


transaction_service = TransactionService()