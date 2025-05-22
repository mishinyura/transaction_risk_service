from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transactions import TransactionModel
from app.models.accounts import AccountModel
from app.schemas.transactions import TransactionCreateSchema


class RiskAnalysisService:
    # Пороговые значения для анализа
    HIGH_RISK_THRESHOLD = 0.80
    AMOUNT_THRESHOLD = 10000
    AMOUNT_INCREASE_THRESHOLD = 3.0  # 300%
    FRAUD_RISK_THRESHOLD = 0.6
    RISK_SCORE_WEIGHTS = {
        'receiver_risk': 0.3,
        'amount_anomaly': 0.3,
        'location_anomaly': 0.2,
        'device_anomaly': 0.2
    }

    def __init__(self):
        self.analysis_window_days = 7

    async def analyze_transaction(
        self,
        transaction: TransactionCreateSchema,
        session: AsyncSession
    ) -> Tuple[float, bool]:
        """
        Анализирует транзакцию и возвращает кортеж (оценка риска, флаг подозрительности)
        """
        risk_score = 0.0
        
        start_date = datetime.now() - timedelta(days=self.analysis_window_days)
        
        receiver_risk = await self._get_account_risk(
            transaction.receiver_account_id, session
        )
        if receiver_risk >= self.HIGH_RISK_THRESHOLD:
            risk_score += self.RISK_SCORE_WEIGHTS['receiver_risk']

        if await self._is_amount_anomaly(transaction, start_date, session):
            risk_score += self.RISK_SCORE_WEIGHTS['amount_anomaly']

        if await self._is_location_anomaly(transaction, start_date, session):
            risk_score += self.RISK_SCORE_WEIGHTS['location_anomaly']

        if await self._is_device_anomaly(transaction, start_date, session):
            risk_score += self.RISK_SCORE_WEIGHTS['device_anomaly']

        is_fraud = risk_score > self.FRAUD_RISK_THRESHOLD

        return risk_score, is_fraud

    async def _get_account_risk(
        self, account_id: str, session: AsyncSession
    ) -> float:
        """Получает уровень риска аккаунта"""
        result = await session.execute(
            select(AccountModel.risk).where(AccountModel.account_id == account_id)
        )
        return result.scalar_one_or_none() or 0.0

    async def _is_amount_anomaly(
        self, 
        transaction: TransactionCreateSchema,
        start_date: datetime,
        session: AsyncSession
    ) -> bool:
        """Проверяет, является ли сумма транзакции аномальной"""
        if transaction.transaction_amount <= self.AMOUNT_THRESHOLD:
            return False

        result = await session.execute(
            select(func.avg(TransactionModel.transaction_amount))
            .where(
                TransactionModel.sender_account_id == transaction.sender_account_id,
                TransactionModel.timestamp >= start_date
            )
        )
        avg_amount = result.scalar_one_or_none() or 0.0

        if avg_amount == 0:
            return False

        return transaction.transaction_amount > (
            avg_amount * self.AMOUNT_INCREASE_THRESHOLD
        )

    async def _is_location_anomaly(
        self,
        transaction: TransactionCreateSchema,
        start_date: datetime,
        session: AsyncSession
    ) -> bool:
        """Проверяет, является ли геолокация аномальной"""
        result = await session.execute(
            select(TransactionModel.geolocation)
            .where(
                TransactionModel.sender_account_id == transaction.sender_account_id,
                TransactionModel.timestamp >= start_date
            )
            .distinct()
        )
        recent_locations = {row[0] for row in result.all()}

        return len(recent_locations) > 0 and transaction.geolocation not in recent_locations

    async def _is_device_anomaly(
        self,
        transaction: TransactionCreateSchema,
        start_date: datetime,
        session: AsyncSession
    ) -> bool:
        """Проверяет, является ли устройство аномальным"""
        result = await session.execute(
            select(TransactionModel.device_user)
            .where(
                TransactionModel.sender_account_id == transaction.sender_account_id,
                TransactionModel.timestamp >= start_date
            )
            .distinct()
        )
        recent_devices = {row[0] for row in result.all()}

        return len(recent_devices) > 0 and transaction.device_user not in recent_devices


risk_analysis_service = RiskAnalysisService()
