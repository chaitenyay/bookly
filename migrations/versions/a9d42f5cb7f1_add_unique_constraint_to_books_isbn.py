"""Add unique constraint to books.isbn

Revision ID: a9d42f5cb7f1
Revises: f333f2e6ce93
Create Date: 2026-02-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a9d42f5cb7f1'
down_revision: Union[str, Sequence[str], None] = 'f333f2e6ce93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_books_isbn', 'books', ['isbn'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_books_isbn', 'books', type_='unique')
