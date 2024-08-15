"""initial schema

Revision ID: a83a54bbc616
Revises: 
Create Date: 2024-08-15 10:08:52.836285+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a83a54bbc616'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('username', sa.Text, unique=True, nullable=False),
        sa.Column('password', sa.Text, nullable=False)
    )

    op.create_table(
        'post',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('author_id', sa.BigInteger, nullable=False),
        sa.Column('created', sa.TIMESTAMP, nullable=False),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('body', sa.Text, nullable=False),
    )
    op.create_foreign_key(
        constraint_name='post_author_id_fkey',
        source_table='post',
        referent_table='user',
        local_cols=['author_id'],
        remote_cols=['id']
    )


def downgrade() -> None:
    # no actual need to remove the base schema
    pass
