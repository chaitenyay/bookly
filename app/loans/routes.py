from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.db.main import get_session
from app.loans.schemas import Loan, LoanCreate, LoanReissue, LoanReturn
from app.loans.service import LoanService


loan_router = APIRouter()
loan_service = LoanService()
access_token_bearer = AccessTokenBearer()


@loan_router.get("/", response_model=List[Loan])
async def read_loans(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    loans = await loan_service.get_all_loans(session)
    return loans


@loan_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Loan,
    dependencies=[Depends(access_token_bearer)],
)
async def create_loan(
    loan: LoanCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_loan = await loan_service.create_loan(loan, session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return new_loan


@loan_router.get("/{loan_uid}", response_model=Loan)
async def read_loan(
    loan_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    loan = await loan_service.get_loan(loan_uid, session)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@loan_router.patch("/{loan_uid}/reissue", status_code=status.HTTP_200_OK, response_model=Loan)
async def reissue_loan(
    loan_uid: uuid.UUID,
    reissue_data: LoanReissue,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    loan = await loan_service.reissue_loan(loan_uid, reissue_data, session)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@loan_router.patch("/{loan_uid}/return", status_code=status.HTTP_200_OK, response_model=Loan)
async def return_loan(
    loan_uid: uuid.UUID,
    return_data: LoanReturn,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    loan = await loan_service.return_loan(loan_uid, return_data, session)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan
