"""merge auth and grocery heads

Revision ID: a1b2c3d4e5f6
Revises: c3f8a1b2d904, c7f2a1b9e4d0
Create Date: 2026-07-28 03:30:00.000000
"""

from typing import Sequence, Union


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = ("c3f8a1b2d904", "c7f2a1b9e4d0")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
