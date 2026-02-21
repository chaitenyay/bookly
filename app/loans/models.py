from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint, text
from sqlmodel import Field, Relationship, SQLModel

from app.books.models import Book
from app.members.models import Member


class Loan(SQLModel, table=True):
    __tablename__ = "loans"
    __table_args__ = (
        UniqueConstraint("book_uid", "member_uid", name="uq_loans_book_member"),
        Index("ix_loans_book_uid", "book_uid"),
        Index("ix_loans_member_uid", "member_uid"),
        Index("ix_loans_borrowed_at", "borrowed_at"),
    )

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
    book_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("books.uid"),
            nullable=False,
        )
    )
    member_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("members.uid"),
            nullable=False,
        )
    )
    book: Optional[Book] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    member: Optional[Member] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    borrowed_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    )
    due_date: datetime | None = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False),
    )
    reissued_at: datetime | None = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True),
    )
    returned_at: datetime | None = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True),
    )
    fine_amount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(pg.NUMERIC(10, 2), nullable=False, server_default=text("0.00")),
    )
    fine_grace_amount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(pg.NUMERIC(10, 2), nullable=False, server_default=text("0.00")),
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)
    )
