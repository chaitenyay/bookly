from typing import List
import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.author.schemas import Author, AuthorCreate, AuthorUpdate
from app.common.error_repsonses import _error_response
from app.common.schemas import APIResponse
from app.author.service import AuthorService
from app.db.main import get_session


author_router = APIRouter()
author_service = AuthorService()
access_token_bearer = AccessTokenBearer()

@author_router.get("/", response_model=APIResponse[List[Author]])
async def read_authors(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    authors = await author_service.get_all_authors(session)
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=authors,
        message="Authors fetched successfully",
        errors=None,
    )


@author_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[Author],
    dependencies=[Depends(access_token_bearer)],
)
async def create_author(
    request: Request,
    author: AuthorCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_author = await author_service.create_author(author, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="AUTHOR_CONFLICT",
            message="Author could not be created",
            details=str(exc),
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_201_CREATED,
        data=new_author,
        message="Author created successfully",
        errors=None,
    )


@author_router.get("/{author_uid}", response_model=APIResponse[Author])
async def read_author(
    request: Request,
    author_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    author = await author_service.get_author(author_uid, session)
    if not author:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="AUTHOR_NOT_FOUND",
            message="Author not found",
            details=f"No author exists with uid {author_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=author,
        message="Author fetched successfully",
        errors=None,
    )


@author_router.patch("/{author_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[Author])
async def update_author(
    request: Request,
    author_uid: uuid.UUID,
    updated_author: AuthorUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        author = await author_service.update_author(author_uid, updated_author, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="AUTHOR_CONFLICT",
            message="Author could not be updated",
            details=str(exc),
        )
    if not author:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="AUTHOR_NOT_FOUND",
            message="Author not found",
            details=f"No author exists with uid {author_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=author,
        message="Author updated successfully",
        errors=None,
    )


@author_router.delete("/{author_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[dict])
async def delete_author(
    request: Request,
    author_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        deleted = await author_service.delete_author(author_uid, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="AUTHOR_CONFLICT",
            message="Author could not be deleted",
            details=str(exc),
        )
    if not deleted:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="AUTHOR_NOT_FOUND",
            message="Author not found",
            details=f"No author exists with uid {author_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data={"author_uid": str(author_uid)},
        message="Author deleted successfully",
        errors=None,
    )
