from sqlmodel import SQLModel, Field, Column, DateTime
import sqlalchemy.dialects.postgresql as pg
from typing import Optional
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            unique=True,
            index=True,
            nullable=False,
            default=uuid.uuid4,
            primary_key=True
        )
    )
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password_hash: str = Field(exclude=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


# class UserCreateModel(SQLModel):
#     username: str
#     email: str
#     password: str



# class UserUpdate(SQLModel):
#     email: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None


# class UserUpdate(SQLModel):
#     email: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     password: Optional[str] = None


# class UserResponse(SQLModel):
#     id: int
#     username: str
#     email: str
#     full_name: Optional[str]
#     is_active: bool
#     created_at: datetime