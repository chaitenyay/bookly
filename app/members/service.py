import uuid

from sqlalchemy.exc import IntegrityError
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.members.models import Member
from app.members.schemas import MemberCreate, MemberUpdate


class MemberService:

    async def get_all_members(self, session: AsyncSession):
        statement = select(Member).order_by(desc(Member.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_member(self, member_uid: uuid.UUID, session: AsyncSession):
        statement = select(Member).where(Member.uid == member_uid)
        result = await session.exec(statement)
        member = result.first()
        return member if member else None

    async def create_member(self, member_data: MemberCreate, session: AsyncSession):
        new_member = Member(**member_data.model_dump())
        session.add(new_member)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Member with this email already exists")
        await session.refresh(new_member)
        return new_member

    async def update_member(self, member_uid: uuid.UUID, member_data: MemberUpdate, session: AsyncSession):
        member = await self.get_member(member_uid, session)
        if not member:
            return None

        for key, value in member_data.model_dump(exclude_unset=True).items():
            setattr(member, key, value)

        session.add(member)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Member with this email already exists")
        await session.refresh(member)
        return member

    async def delete_member(self, member_uid: uuid.UUID, session: AsyncSession):
        member = await self.get_member(member_uid, session)
        if not member:
            return False

        await session.delete(member)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Member cannot be deleted because it is referenced by other records")
        return True
