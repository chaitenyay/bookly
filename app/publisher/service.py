import uuid

from sqlalchemy.exc import IntegrityError
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.publisher.models import Publisher
from app.publisher.schemas import PublisherCreate, PublisherUpdate


class PublisherService:

    async def get_all_publishers(self, session: AsyncSession):
        statement = select(Publisher).order_by(desc(Publisher.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_publisher(self, publisher_uid: uuid.UUID, session: AsyncSession):
        statement = select(Publisher).where(Publisher.uid == publisher_uid)
        result = await session.exec(statement)
        publisher = result.first()
        return publisher if publisher else None

    async def create_publisher(self, publisher_data: PublisherCreate, session: AsyncSession):
        new_publisher = Publisher(**publisher_data.model_dump())
        session.add(new_publisher)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Publisher with this email already exists")
        await session.refresh(new_publisher)
        return new_publisher

    async def update_publisher(self, publisher_uid: uuid.UUID, publisher_data: PublisherUpdate, session: AsyncSession):
        publisher = await self.get_publisher(publisher_uid, session)
        if not publisher:
            return None

        for key, value in publisher_data.model_dump(exclude_unset=True).items():
            setattr(publisher, key, value)

        session.add(publisher)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Publisher with this email already exists")
        await session.refresh(publisher)
        return publisher

    async def delete_publisher(self, publisher_uid: uuid.UUID, session: AsyncSession):
        publisher = await self.get_publisher(publisher_uid, session)
        if not publisher:
            return False

        await session.delete(publisher)
        await session.commit()
        return True
