import math
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionStatus, TransactionType
from app.core.exceptions import DuplicateException, SqlException
from app.models.accounts import AccountModel
from app.databases.accounts import account_crud
from app.schemas.accounts import AccountSchema, AccountRiskSchema
from app.schemas.transactions import TransactionSchema
from app.services.transactions import transaction_service
from app.core.config import settings


class AccountService:
    def __init__(self):
        self.crud = account_crud

    @staticmethod
    def _calculate_account_score(
            send_transactions: list[TransactionSchema], received_transactions: list[TransactionSchema]
    ) -> float:
        all_transactions = send_transactions + received_transactions
        if len(all_transactions) < 5:
            return 50

        transaction_count = len(all_transactions)
        now = max(transaction.transaction_datetime for transaction in all_transactions)
        decay_days = 30
        weighted_count = 0
        
        for transaction in all_transactions:
            age_days = (now - transaction.transaction_datetime).days
            weight = max(0.1, 1 - (age_days / decay_days)) ** 2
            weighted_count += weight
            
        count_score = min(
            weighted_count / settings.score.TRANSACTIONS_COUNT_WEIGHT, 1.0
        ) * settings.score.TRANSACTIONS_COUNT_WEIGHT

        if transaction_count > 1:
            dates = sorted([transaction.transaction_datetime for transaction in all_transactions])
            time_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
            avg_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            if avg_diff > 0:
                freq_score = min(1.0 / avg_diff, 1.0) * settings.score.TRANSACTIONS_FREQUENCY_WEIGHT
            else:
                freq_score = settings.score.TRANSACTIONS_FREQUENCY_WEIGHT
        else:
            freq_score = 0

        successful = sum(1 for t in all_transactions if t.transaction_status == TransactionStatus.SUCCESS)
        quality_score = (successful / transaction_count) * settings.score.TRANSACTIONS_QUALITY_WEIGHT

        type_weights = {
            TransactionType.TRANSFER: 1,
            TransactionType.DEPOSIT: 0.9,
            TransactionType.WITHDRAWAL: 0.8
        }
        type_score = sum(type_weights.get(transaction.transaction_type, 0.5) for transaction in all_transactions)
        type_score = min(type_score / len(all_transactions), settings.score.TRANSACTIONS_TYPE_WEIGHT)
        
        fraud_count = sum(1 for transaction in all_transactions if transaction.fraud_flag)
        if fraud_count / transaction_count > 0.3:
            return 0
        fraud_weight = (
                               fraud_count / (transaction_count * settings.score.TRANSACTIONS_FRAUD_WEIGHT / 100)
                       ) * settings.score.TRANSACTIONS_FRAUD_WEIGHT
        fraud_score = min(fraud_weight, settings.score.TRANSACTIONS_FRAUD_WEIGHT)

        amount_score = 0
        for transaction in all_transactions:
            if transaction.transaction_status == TransactionStatus.SUCCESS:
                amount_score += min(math.log10(transaction.transaction_amount + 1) * 2, 5)
        
        amount_score = min(amount_score, settings.score.TRANSACTIONS_AMOUNT_WEIGHT)
        
        total_score = count_score + freq_score + quality_score + type_score + amount_score - fraud_score
        return max(min(total_score, 100), 0)

    async def get_all_accounts(self, session: AsyncSession) -> list[AccountSchema]:
        accounts = await self.crud.get_all(session=session)
        return accounts

    async def get_account_score(
        self, account_id: str, session: AsyncSession
    ) -> AccountRiskSchema | None:
        account = await self.crud.get_account(
            account_id=account_id, session=session
        )
        if not account:
            return None
            
        send_transactions = await transaction_service.get_account_send_transactions(
            account_id=account.account_id,
            session=session,
        )
        received_transactions = await transaction_service.get_account_received_transactions(
            account_id=account_id,
            session=session,
        )

        return AccountRiskSchema(
            account_id=account.account_id,
            score=self._calculate_account_score(
                send_transactions=send_transactions, received_transactions=received_transactions
            ),
        )

    async def create_account(
            self, account_data: AccountSchema, session: AsyncSession
    ) -> None:
        account = AccountModel(
            account_id=account_data.account_id,
            first_name=account_data.first_name,
            last_name=account_data.last_name,
            middle_name=account_data.middle_name,
            score=account_data.score
        )
        try:
            await self.crud.add(account=account, session=session)
        except SqlException as exc:
            raise DuplicateException(message=str(exc))


account_service = AccountService()