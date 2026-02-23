from typing import List
import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.common.error_repsonses import _error_response
from app.common.schemas import APIResponse
from app.db.main import get_session
from app.publisher.schemas import Publisher, PublisherCreate, PublisherUpdate
from app.publisher.service import PublisherService


publisher_router = APIRouter()
publisher_service = PublisherService()
access_token_bearer = AccessTokenBearer()


@publisher_router.get("/", response_model=APIResponse[List[Publisher]])
async def read_publishers(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    publishers = await publisher_service.get_all_publishers(session)
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=publishers,
        message="Publishers fetched successfully",
        errors=None,
    )


@publisher_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[Publisher],
    dependencies=[Depends(access_token_bearer)],
)
async def create_publisher(
    request: Request,
    publisher: PublisherCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_publisher = await publisher_service.create_publisher(publisher, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="PUBLISHER_CONFLICT",
            message="Publisher could not be created",
            details=str(exc),
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_201_CREATED,
        data=new_publisher,
        message="Publisher created successfully",
        errors=None,
    )


@publisher_router.get("/{publisher_uid}", response_model=APIResponse[Publisher])
async def read_publisher(
    request: Request,
    publisher_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    publisher = await publisher_service.get_publisher(publisher_uid, session)
    if not publisher:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PUBLISHER_NOT_FOUND",
            message="Publisher not found",
            details=f"No publisher exists with uid {publisher_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=publisher,
        message="Publisher fetched successfully",
        errors=None,
    )


@publisher_router.patch("/{publisher_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[Publisher])
async def update_publisher(
    request: Request,
    publisher_uid: uuid.UUID,
    updated_publisher: PublisherUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        publisher = await publisher_service.update_publisher(publisher_uid, updated_publisher, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="PUBLISHER_CONFLICT",
            message="Publisher could not be updated",
            details=str(exc),
        )
    if not publisher:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PUBLISHER_NOT_FOUND",
            message="Publisher not found",
            details=f"No publisher exists with uid {publisher_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=publisher,
        message="Publisher updated successfully",
        errors=None,
    )


@publisher_router.delete("/{publisher_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[dict])
async def delete_publisher(
    request: Request,
    publisher_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        deleted = await publisher_service.delete_publisher(publisher_uid, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="PUBLISHER_CONFLICT",
            message="Publisher could not be deleted",
            details=str(exc),
        )
    if not deleted:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PUBLISHER_NOT_FOUND",
            message="Publisher not found",
            details=f"No publisher exists with uid {publisher_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data={"publisher_uid": str(publisher_uid)},
        message="Publisher deleted successfully",
        errors=None,
    )
