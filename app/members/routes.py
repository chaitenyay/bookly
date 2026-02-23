from typing import List
import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.common.error_repsonses import _error_response
from app.common.schemas import APIResponse
from app.db.main import get_session
from app.members.schemas import Member, MemberCreate, MemberUpdate
from app.members.service import MemberService


member_router = APIRouter()
member_service = MemberService()
access_token_bearer = AccessTokenBearer()


@member_router.get("/", response_model=APIResponse[List[Member]])
async def read_members(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    members = await member_service.get_all_members(session)
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=members,
        message="Members fetched successfully",
        errors=None,
    )


@member_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[Member],
    dependencies=[Depends(access_token_bearer)],
)
async def create_member(
    request: Request,
    member: MemberCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_member = await member_service.create_member(member, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="MEMBER_CONFLICT",
            message="Member could not be created",
            details=str(exc),
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_201_CREATED,
        data=new_member,
        message="Member created successfully",
        errors=None,
    )


@member_router.get("/{member_uid}", response_model=APIResponse[Member])
async def read_member(
    request: Request,
    member_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    member = await member_service.get_member(member_uid, session)
    if not member:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="MEMBER_NOT_FOUND",
            message="Member not found",
            details=f"No member exists with uid {member_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=member,
        message="Member fetched successfully",
        errors=None,
    )


@member_router.patch("/{member_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[Member])
async def update_member(
    request: Request,
    member_uid: uuid.UUID,
    updated_member: MemberUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        member = await member_service.update_member(member_uid, updated_member, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="MEMBER_CONFLICT",
            message="Member could not be updated",
            details=str(exc),
        )
    if not member:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="MEMBER_NOT_FOUND",
            message="Member not found",
            details=f"No member exists with uid {member_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=member,
        message="Member updated successfully",
        errors=None,
    )


@member_router.delete("/{member_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[dict])
async def delete_member(
    request: Request,
    member_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        deleted = await member_service.delete_member(member_uid, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="MEMBER_CONFLICT",
            message="Member could not be deleted",
            details=str(exc),
        )
    if not deleted:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="MEMBER_NOT_FOUND",
            message="Member not found",
            details=f"No member exists with uid {member_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data={"member_uid": str(member_uid)},
        message="Member deleted successfully",
        errors=None,
    )
