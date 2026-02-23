from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.exc import IntegrityError
import uuid

from app.author.models import Author
from app.author.schemas import AuthorCreate, AuthorUpdate


class AuthorService:

    async def get_all_authors(self, session: AsyncSession):
        statement = select(Author).order_by(desc(Author.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_author(self, author_uid: uuid.UUID, session: AsyncSession):
        statement = select(Author).where(Author.uid == author_uid)
        result = await session.exec(statement)
        author = result.first()
        return author if author else None

    async def create_author(self, author_data: AuthorCreate, session: AsyncSession):
        new_author = Author(**author_data.model_dump())
        session.add(new_author)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Author with this email already exists")
        await session.refresh(new_author)
        return new_author

    async def update_author(self, author_uid: uuid.UUID, author_data: AuthorUpdate, session: AsyncSession):
        author = await self.get_author(author_uid, session)
        if not author:
            return None

        for key, value in author_data.model_dump(exclude_unset=True).items():
            setattr(author, key, value)

        session.add(author)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Author with this email already exists")
        await session.refresh(author)
        return author

    async def delete_author(self, author_uid: uuid.UUID, session: AsyncSession):
        author = await self.get_author(author_uid, session)
        if not author:
            return False

        await session.delete(author)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Author cannot be deleted because it is referenced by other records")
        return True
