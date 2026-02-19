from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from typing import Optional
from datetime import datetime
import uuid


class Member(SQLModel, table=True):
    __tablename__ = "members"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            unique=True,
            index=True,
            nullable=False,
            default=uuid.uuid4,
            primary_key=True,
        )
    )
    first_name: str = Field(default=None, max_length=50)
    last_name: str = Field(default=None, max_length=50)
    email: str = Field(index=True, unique=True, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    join_date: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now)
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self):
        return f"<Member {self.name} ({self.email})>"