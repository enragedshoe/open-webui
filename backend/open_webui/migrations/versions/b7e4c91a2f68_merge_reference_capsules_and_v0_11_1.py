"""merge reference capsules and v0.11.1 migration heads

Revision ID: b7e4c91a2f68
Revises: a4c9d2e7f1b6, d4c1a8e37b62
Create Date: 2026-08-28 00:00:00

"""

from collections.abc import Sequence

revision: str = 'b7e4c91a2f68'
down_revision: tuple[str, str] = ('a4c9d2e7f1b6', 'd4c1a8e37b62')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
