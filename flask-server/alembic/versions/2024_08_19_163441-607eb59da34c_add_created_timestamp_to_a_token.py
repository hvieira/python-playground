"""add created timestamp to a token

Revision ID: 607eb59da34c
Revises: 4dcf0e4ac473
Create Date: 2024-08-19 16:34:41.312968+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '607eb59da34c'
down_revision: Union[str, None] = '4dcf0e4ac473'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user_token',
        sa.Column('created', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.func.now(), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_column(
        'user_token',
        'created'
    )
