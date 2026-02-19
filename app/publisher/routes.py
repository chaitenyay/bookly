from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.db.main import get_session
from app.publisher.schemas import Publisher, PublisherCreate, PublisherUpdate
from app.publisher.service import PublisherService


publisher_router = APIRouter()
publisher_service = PublisherService()
access_token_bearer = AccessTokenBearer()


@publisher_router.get("/", response_model=List[Publisher])
async def read_publishers(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    publishers = await publisher_service.get_all_publishers(session)
    return publishers


@publisher_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Publisher,
    dependencies=[Depends(access_token_bearer)],
)
async def create_publisher(
    publisher: PublisherCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_publisher = await publisher_service.create_publisher(publisher, session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return new_publisher


@publisher_router.get("/{publisher_uid}", response_model=Publisher)
async def read_publisher(
    publisher_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    publisher = await publisher_service.get_publisher(publisher_uid, session)
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
    return publisher


@publisher_router.patch("/{publisher_uid}", status_code=status.HTTP_200_OK, response_model=Publisher)
async def update_publisher(
    publisher_uid: uuid.UUID,
    updated_publisher: PublisherUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        publisher = await publisher_service.update_publisher(publisher_uid, updated_publisher, session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
    return publisher


@publisher_router.delete("/{publisher_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publisher(
    publisher_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    deleted = await publisher_service.delete_publisher(publisher_uid, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Publisher deleted successfully")
