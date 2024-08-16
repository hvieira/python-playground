"""post created  with timezone

Revision ID: 4dcf0e4ac473
Revises: f73fa180bde8
Create Date: 2024-08-16 18:03:09.332521+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4dcf0e4ac473'
down_revision: Union[str, None] = 'f73fa180bde8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'post',
        'created',
        nullable=False,
        type_=sa.TIMESTAMP(timezone=True))


def downgrade() -> None:
    op.alter_column(
        'post',
        'created',
        nullable=False,
        type_=sa.TIMESTAMP(timezone=False))
