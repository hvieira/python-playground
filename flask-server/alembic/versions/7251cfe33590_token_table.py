"""token table

Revision ID: 7251cfe33590
Revises: a83a54bbc616
Create Date: 2024-08-16 10:23:10.373854+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7251cfe33590'
down_revision: Union[str, None] = 'a83a54bbc616'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_token_table_name = 'user_token'


def upgrade() -> None:
    op.create_table(
        user_token_table_name,
        sa.Column('user_id', sa.BigInteger, nullable=False),
        sa.Column('token', sa.Text, unique=True, nullable=False),
        sa.Column('expiry', sa.TIMESTAMP, nullable=False)
    )
    op.create_primary_key(
        constraint_name=f'{user_token_table_name}_pk',
        table_name=user_token_table_name,
        columns=['user_id', 'token']
    )


def downgrade() -> None:
    op.drop_table(user_token_table_name)
