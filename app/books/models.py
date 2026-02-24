from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
import sqlalchemy.dialects.postgresql as pg
from typing import Optional
from datetime import datetime
from app.author.models import Author
from app.publisher.models import Publisher
import uuid


class Book(SQLModel, table=True):
    __tablename__ = "books"
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
    title: str = Field(..., min_length=1, max_length=255)
    author_uid: Optional[uuid.UUID] = Field(foreign_key="authors.uid", nullable=True, default=None)
    publisher_uid: Optional[uuid.UUID] = Field(foreign_key="publishers.uid", nullable=True, default=None)
    isbn: str = Field(..., min_length=10, max_length=20, unique=True, index=True)
    description: Optional[str] = None
    published_date: Optional[datetime] = None
    pages: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, max_length=50)
    available_copies: int = Field(default=0, ge=0)
    author: Optional[Author] = Relationship(back_populates="books", sa_relationship_kwargs={"lazy": "selectin"})
    publisher: Optional[Publisher] = Relationship(back_populates="books", sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"
