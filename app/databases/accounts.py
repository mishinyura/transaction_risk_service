from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import SqlException
from app.models.accounts import AccountModel
from app.schemas.accounts import AccountSchema, AccountRiskSchema
from app.databases.base_crud import BaseCRUD


class AccountCRUD(BaseCRUD):
    async def get_risk(self, account_id: int, session: AsyncSession):
        result = await session.execute(select(AccountModel.risk).where(account_id == AccountModel.account_id))
        risk = result.scalar_one_or_none()
        return AccountRiskSchema.model_validate({'risk': risk})

    async def get_all(self, session: AsyncSession) -> list[AccountSchema] | list:
        result = await session.execute(select(AccountModel))
        accounts = result.scalars().all()
        return [AccountSchema.model_validate(account) for account in accounts]

    async def add(self, account: AccountModel, session: AsyncSession) -> None:
        try:
            session.add(account)
            await session.commit()
        except SQLAlchemyError as exc:
            await session.rollback()
            raise SqlException(message=str(exc))


account_crud = AccountCRUD()