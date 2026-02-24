from sqlmodel.ext.asyncio.session import AsyncSession
from app.books.schemas import BookCreateModel, BookUpdateModel
from app.books.models import Book
from sqlmodel import select, desc
from sqlalchemy.exc import IntegrityError
from typing import Optional
import uuid


class BookService:

    # def __init__(self, book_repository):
    #     self.book_repository = book_repository

    async def get_all_books(
        self,
        session: AsyncSession,
        title: Optional[str] = None,
        author_uid: Optional[uuid.UUID] = None,
        publisher_uid: Optional[uuid.UUID] = None,
        isbn: Optional[str] = None,
    ):
        # return self.book_repository.get_all_books(session)
        statement = select(Book).order_by(desc(Book.created_at))
        if title:
            statement = statement.where(Book.title.ilike(f"%{title}%"))
        if author_uid:
            statement = statement.where(Book.author_uid == author_uid)
        if publisher_uid:
            statement = statement.where(Book.publisher_uid == publisher_uid)
        if isbn:
            statement = statement.where(Book.isbn == isbn)
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        # return self.book_repository.get_book_by_id(book_id, session)
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book else None
    
    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        # return self.book_repository.create_book(book_data, session)
        existing_book_stmt = select(Book).where(Book.isbn == book_data.isbn)
        existing_book_result = await session.exec(existing_book_stmt)
        if existing_book_result.first():
            raise ValueError(f"Book with ISBN '{book_data.isbn}' already exists")

        new_book = Book(**book_data.model_dump())
        session.add(new_book)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Book data conflicts with existing records")
        await session.refresh(new_book)
        return new_book

    async def update_book(self, book_uid: str, book_data: BookUpdateModel, session: AsyncSession):
        # return self.book_repository.update_book(book_id, book_data, session)
        book = await self.get_book(book_uid, session)
        if not book:
            return None
        for key, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        session.add(book)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Book data conflicts with existing records")
        await session.refresh(book)
        return book
    
    async def delete_book(self, book_uid: str, session: AsyncSession):
        # return self.book_repository.delete_book(book_id, session)
        book = await self.get_book(book_uid, session)
        if not book:
            return False
        await session.delete(book)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Book cannot be deleted because it is referenced by other records")
        return True
