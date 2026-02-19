from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
import uuid
from app.db.main import get_session
from app.books.service import BookService
from app.books.schemas import Book, BookCreateModel, BookUpdateModel
from app.auth.dependencies import AccessTokenBearer


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()

# Define API endpoints for book management
@book_router.get("/", response_model=List[Book])
async def read_books(session: AsyncSession = Depends(get_session),token_details: dict = Depends(access_token_bearer)):
    books = await book_service.get_all_books(session)
    return books

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[Depends(access_token_bearer)])
async def create_book(book: BookCreateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    new_book = await book_service.create_book(book, session)
    return new_book


@book_router.get("/{book_uid}")
async def read_book(book_uid: uuid.UUID, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    book = await book_service.get_book(book_uid, session)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@book_router.patch("/{book_uid}", status_code=status.HTTP_200_OK, response_model=Book)
async def update_book(book_uid: uuid.UUID, updated_book: BookUpdateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    book = await book_service.update_book(book_uid, updated_book, session)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book
    


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: uuid.UUID, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    deleted = await book_service.delete_book(book_uid, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Book deleted successfully")