from sqlalchemy.ext.asyncio import AsyncSession

# from app.clients.base_payment_client import base_payment_client
# from app.exceptions import DuplicateException, SqlException
from app.models.transactions import TransactionModel
from app.databases.transactions import transaction_crud
from app.schemas.transactions import TransactionSchema
from app.core.enums import TransactionStatus, TransactionType


class TransactionService:
    def __init__(self):
        self.crud = transaction_crud

    async def get_all_payments(self, session: AsyncSession) -> list[TransactionSchema]:
        payments = await self.crud.get_all(session=session)
        return payments

    async def get_transaction_by_transaction_id(
        self, transaction_id: str, session: AsyncSession
    ) -> TransactionSchema | None:
        transaction = await self.crud.get_transaction(
            transaction_id=transaction_id, session=session
        )
        return transaction

    # async def create_transaction(
    #     self, session: AsyncSession, transaction_data: PaymentSchema
    # ) -> None:
    #     payment = Payment(
    #         sender_account_id=transaction_data.sender_account_id,
    #         receiver_account_id=transaction_data.receiver_account_id,
    #         transaction_amount=transaction_data.transaction_amount,
    #         transaction_type=transaction_data.transaction_type,
    #         timestamp=transaction_data.timestamp,
    #         transaction_status=TransactionStatus.SUCCESS,
    #         geolocation=transaction_data.geolocation,
    #         device_user=transaction_data.device_user
    #     )
    #     try:
    #         await self.repo.add(payment=payment, session=session)
    #     except SqlException as exc:
    #         raise DuplicateException(message=str(exc))
    #
    #     result = await base_payment_client.post_base_payment(payment_data=payment_data)
    #
    #     try:
    #         await self.repo.update_payment_status(
    #             payment_id=payment_data.payment_id,
    #             payment_status=result.status,
    #             session=session,
    #         )
    #     except SqlException as exc:
    #         # logger.error(
    #         #     f"Something went wrong when updating payment status. Current status is {result.status}"
    #         # )
    #         raise DuplicateException(message=str(exc))


transaction_service = TransactionService()