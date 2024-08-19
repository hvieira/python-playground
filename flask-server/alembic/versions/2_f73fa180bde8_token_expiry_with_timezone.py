"""token expiry with timezone

Revision ID: f73fa180bde8
Revises: 7251cfe33590
Create Date: 2024-08-16 12:24:28.815219+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f73fa180bde8'
down_revision: Union[str, None] = '7251cfe33590'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'user_token',
        'expiry',
        nullable=False,
        type_=sa.TIMESTAMP(timezone=True))


def downgrade() -> None:
        op.alter_column(
        'user_token',
        'expiry',
        nullable=False,
        type_=sa.TIMESTAMP(timezone=False))
