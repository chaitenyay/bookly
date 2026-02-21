from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.author.schemas import Author
from app.publisher.schemas import Publisher
import uuid

class BookBaseModel(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author_uid: uuid.UUID = Field(..., foreign_key="authors.uid")
    publisher_uid: Optional[uuid.UUID] = Field(None, foreign_key="publishers.uid")
    isbn: str = Field(..., min_length=10, max_length=20)
    description: Optional[str] = None
    published_date: Optional[datetime] = None
    pages: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, max_length=50)

class BookCreateModel(BookBaseModel):
    pass

class BookUpdateModel(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author_uid: Optional[uuid.UUID] = Field(None, foreign_key="authors.uid")
    publisher_uid: Optional[uuid.UUID] = Field(None, foreign_key="publishers.uid")
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    description: Optional[str] = None
    published_date: Optional[datetime] = None
    pages: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, max_length=50)

class Book(BookBaseModel):
    uid: uuid.UUID
    author: Optional[Author] = None
    publisher: Optional[Publisher] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class BookForLoan(BaseModel):
    uid: uuid.UUID
    title: str
    isbn: str

    class Config:
        from_attributes = True
