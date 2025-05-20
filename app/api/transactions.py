import json

from fastapi import APIRouter, Depends
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_409_CONFLICT
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException
from app.schemas.transactions import TransactionSchema, TransactionCreateSchema
from app.services.transactions import transaction_service
from app.core.db import get_session

transactions_router = APIRouter(tags=["transactions"])


@transactions_router.get("/", response_model=list[TransactionSchema] | None)
async def get_transactions(session: AsyncSession = Depends(get_session)):
    transactions = await transaction_service.get_all_payments(session=session)
    if not transactions:
        return Response(status_code=HTTP_404_NOT_FOUND)
    return transactions


@transactions_router.get("/{transaction_id}", response_model=TransactionSchema | None)
async def get_transaction_by_id(
    transaction_id: int, session: AsyncSession = Depends(get_session)
):
    payment = await transaction_service.get_transaction_by_transaction_id(
        transaction_id=transaction_id, session=session
    )
    if not payment:
        return Response(status_code=HTTP_404_NOT_FOUND)
    return payment


@transactions_router.post("/")
async def create_transaction(
    transaction_data: TransactionCreateSchema, session: AsyncSession = Depends(get_session)
):
    try:
        for key in transaction_data:
            print(key, '|')
        await transaction_service.create_transaction(
            session=session, transaction_data=transaction_data
        )
    except DuplicateException:
        return Response(status_code=HTTP_409_CONFLICT)
    return Response(status_code=HTTP_201_CREATED)