from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.db.main import get_session
from app.members.schemas import Member, MemberCreate, MemberUpdate
from app.members.service import MemberService


member_router = APIRouter()
member_service = MemberService()
access_token_bearer = AccessTokenBearer()


@member_router.get("/", response_model=List[Member])
async def read_members(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    members = await member_service.get_all_members(session)
    return members


@member_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Member,
    dependencies=[Depends(access_token_bearer)],
)
async def create_member(
    member: MemberCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_member = await member_service.create_member(member, session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return new_member


@member_router.get("/{member_uid}", response_model=Member)
async def read_member(
    member_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    member = await member_service.get_member(member_uid, session)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@member_router.patch("/{member_uid}", status_code=status.HTTP_200_OK, response_model=Member)
async def update_member(
    member_uid: uuid.UUID,
    updated_member: MemberUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        member = await member_service.update_member(member_uid, updated_member, session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@member_router.delete("/{member_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    deleted = await member_service.delete_member(member_uid, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Member deleted successfully")
