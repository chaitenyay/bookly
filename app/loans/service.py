import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.loans.models import Loan
from app.loans.schemas import LoanCreate, LoanReissue, LoanReturn


class LoanService:

    async def get_all_loans(self, session: AsyncSession):
        statement = (
            select(Loan)
            .options(selectinload(Loan.book), selectinload(Loan.member))
            .order_by(desc(Loan.created_at))
        )
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
        new_loan = Loan(**loan_data.model_dump())
        session.add(new_loan)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Loan already exists for this book and member")
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

        loan.returned_at = return_data.returned_at
        loan.fine_amount = return_data.fine_amount
        loan.fine_grace_amount = return_data.fine_grace_amount

        session.add(loan)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Loan could not be returned due to a data conflict")
        await session.refresh(loan)
        return loan
