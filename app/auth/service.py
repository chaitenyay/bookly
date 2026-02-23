from typing import Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.auth.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.auth.schemas import UserCreateModel
from app.auth.utils import generate_password_hash
from sqlalchemy.exc import IntegrityError



class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user if user else None
    
    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return True if user else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        new_user = User(**user_data.model_dump())
        new_user.password_hash = generate_password_hash(user_data.password)
        session.add(new_user)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("User with this username or email already exists")
        await session.refresh(new_user)
        return new_user 
    
