from fastapi import APIRouter, Depends
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_409_CONFLICT
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException
from app.schemas.accounts import AccountSchema, AccountRiskSchema
from app.services.accounts import account_service
from app.core.db import get_session

accounts_router = APIRouter(tags=["accounts"])


@accounts_router.get("/", response_model=list[AccountSchema] | None)
async def get_accounts(session: AsyncSession = Depends(get_session)):
    accounts = await account_service.get_all_accounts(session=session)
    if not accounts:
        return Response(status_code=HTTP_404_NOT_FOUND)
    return accounts


@accounts_router.get("/score/{account_id}", response_model=AccountRiskSchema | None)
async def get_account_score(
    account_id: str, session: AsyncSession = Depends(get_session)
):
    account = await account_service.get_account_score(
        account_id=account_id, session=session
    )
    if not account:
        return Response(status_code=HTTP_404_NOT_FOUND)
    return account


@accounts_router.post("/")
async def create_account(
    account_data: AccountSchema, session: AsyncSession = Depends(get_session)
):
    try:
        await account_service.create_account(
            session=session, account_data=account_data
        )
    except DuplicateException:
        return Response(status_code=HTTP_409_CONFLICT)
    return Response(status_code=HTTP_201_CREATED)