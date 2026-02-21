from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from pydantic import BaseModel, Field

from app.books.schemas import BookForLoan
from app.members.schemas import MemberForLoan


class LoanBase(BaseModel):
    book_uid: uuid.UUID = Field(..., foreign_key="books.uid")
    member_uid: uuid.UUID = Field(..., foreign_key="members.uid")
    borrowed_at: datetime = Field(default_factory=datetime.now)
    due_date: datetime
    reissued_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None


class LoanCreate(LoanBase):
    pass


class LoanReissue(BaseModel):
    due_date: datetime
    reissued_at: datetime = Field(default_factory=datetime.now)


class LoanReturn(BaseModel):
    returned_at: datetime = Field(default_factory=datetime.now)
    fine_amount: Decimal = Decimal("0.00")
    fine_grace_amount: Decimal = Decimal("0.00")

class Loan(LoanBase):
    uid: uuid.UUID
    book: Optional[BookForLoan] = None
    member: Optional[MemberForLoan] = None
    fine_amount: Decimal = Decimal("0.00")
    fine_grace_amount: Decimal = Decimal("0.00")
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
