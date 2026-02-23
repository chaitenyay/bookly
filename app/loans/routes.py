from typing import List
import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.common.error_repsonses import _error_response
from app.common.schemas import APIResponse
from app.db.main import get_session
from app.loans.schemas import Loan, LoanCreate, LoanReissue, LoanReturn
from app.loans.service import LoanService


loan_router = APIRouter()
loan_service = LoanService()
access_token_bearer = AccessTokenBearer()


@loan_router.get("/", response_model=APIResponse[List[Loan]])
async def read_loans(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    loans = await loan_service.get_all_loans(session)
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=loans,
        message="Loans fetched successfully",
        errors=None,
    )


@loan_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[Loan],
    dependencies=[Depends(access_token_bearer)],
)
async def create_loan(
    request: Request,
    loan: LoanCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_loan = await loan_service.create_loan(loan, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="LOAN_CONFLICT",
            message="Loan could not be created",
            details=str(exc),
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_201_CREATED,
        data=new_loan,
        message="Loan created successfully",
        errors=None,
    )


@loan_router.get("/{loan_uid}", response_model=APIResponse[Loan])
async def read_loan(
    request: Request,
    loan_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    loan = await loan_service.get_loan(loan_uid, session)
    if not loan:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="LOAN_NOT_FOUND",
            message="Loan not found",
            details=f"No loan exists with uid {loan_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=loan,
        message="Loan fetched successfully",
        errors=None,
    )


@loan_router.patch("/{loan_uid}/reissue", status_code=status.HTTP_200_OK, response_model=APIResponse[Loan])
async def reissue_loan(
    request: Request,
    loan_uid: uuid.UUID,
    reissue_data: LoanReissue,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        loan = await loan_service.reissue_loan(loan_uid, reissue_data, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="LOAN_CONFLICT",
            message="Loan could not be reissued",
            details=str(exc),
        )
    if not loan:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="LOAN_NOT_FOUND",
            message="Loan not found",
            details=f"No loan exists with uid {loan_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=loan,
        message="Loan reissued successfully",
        errors=None,
    )


@loan_router.patch("/{loan_uid}/return", status_code=status.HTTP_200_OK, response_model=APIResponse[Loan])
async def return_loan(
    request: Request,
    loan_uid: uuid.UUID,
    return_data: LoanReturn,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        loan = await loan_service.return_loan(loan_uid, return_data, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="LOAN_CONFLICT",
            message="Loan could not be returned",
            details=str(exc),
        )
    if not loan:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="LOAN_NOT_FOUND",
            message="Loan not found",
            details=f"No loan exists with uid {loan_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=loan,
        message="Loan returned successfully",
        errors=None,
    )
