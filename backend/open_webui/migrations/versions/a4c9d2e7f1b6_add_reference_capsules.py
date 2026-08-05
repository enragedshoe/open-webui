"""add reference capsules

Revision ID: a4c9d2e7f1b6
Revises: f0bd01a18a3d
Create Date: 2026-08-03 13:45:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'a4c9d2e7f1b6'
down_revision: str | None = 'f0bd01a18a3d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'reference_capsule',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('source_chat_id', sa.String(), nullable=False),
        sa.Column('source_title', sa.Text(), nullable=False),
        sa.Column('source_updated_at', sa.BigInteger(), nullable=False),
        sa.Column('source_hash', sa.String(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('facts', sa.JSON(), nullable=False),
        sa.Column('decisions', sa.JSON(), nullable=False),
        sa.Column('constraints', sa.JSON(), nullable=False),
        sa.Column('open_questions', sa.JSON(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('user_id', 'source_chat_id', name='uq_reference_capsule_user_source'),
    )
    op.create_index('ix_reference_capsule_user_id', 'reference_capsule', ['user_id'])
    op.create_index('ix_reference_capsule_updated_at', 'reference_capsule', ['updated_at'])


def downgrade() -> None:
    op.drop_index('ix_reference_capsule_updated_at', table_name='reference_capsule')
    op.drop_index('ix_reference_capsule_user_id', table_name='reference_capsule')
    op.drop_table('reference_capsule')
