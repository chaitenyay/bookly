import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.books.models import Book
from app.loans.models import Loan
from app.loans.schemas import LoanCreate, LoanReissue, LoanReturn


class LoanService:

    async def get_all_loans(
        self,
        session: AsyncSession,
        book_uid: uuid.UUID | None = None,
        member_uid: uuid.UUID | None = None,
    ):
        statement = (
            select(Loan)
            .options(selectinload(Loan.book), selectinload(Loan.member))
            .order_by(desc(Loan.created_at))
        )
        if book_uid:
            statement = statement.where(Loan.book_uid == book_uid)
        if member_uid:
            statement = statement.where(Loan.member_uid == member_uid)
        result = await session.exec(statement)
        return result.all()

    async def get_loan(self, loan_uid: uuid.UUID, session: AsyncSession):
        statement = (
            select(Loan)
            .options(selectinload(Loan.book), selectinload(Loan.member))
            .where(Loan.uid == loan_uid)
        )
        result = await session.exec(statement)
        loan = result.first()
        return loan if loan else None

    async def create_loan(self, loan_data: LoanCreate, session: AsyncSession):
        book_statement = select(Book).where(Book.uid == loan_data.book_uid)
        book_result = await session.exec(book_statement)
        book = book_result.first()
        if not book:
            raise ValueError("Book not found")
        if book.available_copies <= 0:
            raise ValueError("Book is out of stock")

        active_loan_statement = select(Loan).where(
            Loan.book_uid == loan_data.book_uid,
            Loan.member_uid == loan_data.member_uid,
            Loan.returned_at.is_(None),
        )
        active_loan_result = await session.exec(active_loan_statement)
        active_loan = active_loan_result.first()
        if active_loan:
            raise ValueError("Member already has an active loan for this book")

        new_loan = Loan(**loan_data.model_dump())
        book.available_copies -= 1
        session.add(new_loan)
        session.add(book)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Loan could not be created due to a data conflict")
        await session.refresh(new_loan)
        return new_loan

    async def reissue_loan(self, loan_uid: uuid.UUID, reissue_data: LoanReissue, session: AsyncSession):
        loan = await self.get_loan(loan_uid, session)
        if not loan:
            return None

        loan.due_date = reissue_data.due_date
        loan.reissued_at = reissue_data.reissued_at

        session.add(loan)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Loan could not be reissued due to a data conflict")
        await session.refresh(loan)
        return loan

    async def return_loan(self, loan_uid: uuid.UUID, return_data: LoanReturn, session: AsyncSession):
        loan = await self.get_loan(loan_uid, session)
        if not loan:
            return None
        if loan.returned_at is not None:
            raise ValueError("Loan has already been returned")

        book_statement = select(Book).where(Book.uid == loan.book_uid)
        book_result = await session.exec(book_statement)
        book = book_result.first()
        if not book:
            raise ValueError("Book not found")

        loan.returned_at = return_data.returned_at
        loan.fine_amount = return_data.fine_amount
        loan.fine_grace_amount = return_data.fine_grace_amount
        book.available_copies += 1

        session.add(loan)
        session.add(book)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Loan could not be returned due to a data conflict")
        await session.refresh(loan)
        return loan
