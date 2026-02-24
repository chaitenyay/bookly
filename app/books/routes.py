from fastapi import APIRouter, status, Depends, Request, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
import uuid
from app.db.main import get_session
from app.books.service import BookService
from app.books.schemas import Book, BookCreateModel, BookUpdateModel
from app.auth.dependencies import AccessTokenBearer
from app.common.error_repsonses import _error_response
from app.common.schemas import APIResponse


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


# Define API endpoints for book management
@book_router.get("/", response_model=APIResponse[List[Book]])
async def read_books(
    title: Optional[str] = Query(None, min_length=1, max_length=255),
    author_uid: Optional[uuid.UUID] = None,
    publisher_uid: Optional[uuid.UUID] = None,
    isbn: Optional[str] = Query(None, min_length=10, max_length=20),
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(
        session=session,
        title=title,
        author_uid=author_uid,
        publisher_uid=publisher_uid,
        isbn=isbn,
    )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=books,
        message="Books fetched successfully",
        errors=None,
    )

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=APIResponse[Book], dependencies=[Depends(access_token_bearer)])
async def create_book(request: Request, book: BookCreateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    try:
        new_book = await book_service.create_book(book, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="BOOK_CONFLICT",
            message="Book could not be created",
            details=str(exc),
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_201_CREATED,
        data=new_book,
        message="Book created successfully",
        errors=None,
    )


@book_router.get("/{book_uid}", response_model=APIResponse[Book])
async def read_book(request: Request, book_uid: uuid.UUID, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    book = await book_service.get_book(book_uid, session)
    if not book:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="BOOK_NOT_FOUND",
            message="Book not found",
            details=f"No book exists with uid {book_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=book,
        message="Book fetched successfully",
        errors=None,
    )


@book_router.patch("/{book_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[Book])
async def update_book(request: Request, book_uid: uuid.UUID, updated_book: BookUpdateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    try:
        book = await book_service.update_book(book_uid, updated_book, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="BOOK_CONFLICT",
            message="Book could not be updated",
            details=str(exc),
        )
    if not book:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="BOOK_NOT_FOUND",
            message="Book not found",
            details=f"No book exists with uid {book_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data=book,
        message="Book updated successfully",
        errors=None,
    )
    


@book_router.delete("/{book_uid}", status_code=status.HTTP_200_OK, response_model=APIResponse[dict])
async def delete_book(request: Request, book_uid: uuid.UUID, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    try:
        deleted = await book_service.delete_book(book_uid, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="BOOK_CONFLICT",
            message="Book could not be deleted",
            details=str(exc),
        )
    if not deleted:
        return _error_response(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="BOOK_NOT_FOUND",
            message="Book not found",
            details=f"No book exists with uid {book_uid}",
        )
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data={"book_uid": str(book_uid)},
        message="Book deleted successfully",
        errors=None,
    )
