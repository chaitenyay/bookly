from sqlmodel.ext.asyncio.session import AsyncSession
from app.books.schemas import BookCreateModel, BookUpdateModel
from app.books.models import Book
from sqlmodel import select, desc


class BookService:

    # def __init__(self, book_repository):
    #     self.book_repository = book_repository

    async def get_all_books(self, session: AsyncSession):
        # return self.book_repository.get_all_books(session)
        statement = select(Book).order_by(desc(Book.created_at))
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
            new_book = Book(**book_data.model_dump())
            session.add(new_book)
            await session.commit()
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
        await session.commit()
        await session.refresh(book)
        return book
    
    async def delete_book(self, book_uid: str, session: AsyncSession):
        # return self.book_repository.delete_book(book_id, session)
        book = await self.get_book(book_uid, session)
        if not book:
            return False
        await session.delete(book)
        await session.commit()
        return True