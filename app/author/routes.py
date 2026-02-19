from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer
from app.author.schemas import Author, AuthorCreate, AuthorUpdate
from app.author.service import AuthorService
from app.db.main import get_session


author_router = APIRouter()
author_service = AuthorService()
access_token_bearer = AccessTokenBearer()


@author_router.get("/", response_model=List[Author])
async def read_authors(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    authors = await author_service.get_all_authors(session)
    return authors


@author_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Author,
    dependencies=[Depends(access_token_bearer)],
)
async def create_author(
    author: AuthorCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        new_author = await author_service.create_author(author, session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return new_author


@author_router.get("/{author_uid}", response_model=Author)
async def read_author(
    author_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    author = await author_service.get_author(author_uid, session)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return author


@author_router.patch("/{author_uid}", status_code=status.HTTP_200_OK, response_model=Author)
async def update_author(
    author_uid: uuid.UUID,
    updated_author: AuthorUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        author = await author_service.update_author(author_uid, updated_author, session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return author


@author_router.delete("/{author_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    deleted = await author_service.delete_author(author_uid, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Author deleted successfully")
