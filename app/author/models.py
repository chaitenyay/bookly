from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
import sqlalchemy.dialects.postgresql as pg
from typing import Optional, List
from datetime import datetime
from app.books import models
import uuid


class Author(SQLModel, table=True):
    __tablename__ = "authors"
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
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(index=True, unique=True)
    books: List["models.Book"] = Relationship(back_populates="author", sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self):
        return f"<Author {self.first_name} {self.last_name} ({self.email})>"