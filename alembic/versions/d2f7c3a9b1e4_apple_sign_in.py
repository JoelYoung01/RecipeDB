"""apple_sign_in

Revision ID: d2f7c3a9b1e4
Revises: a1b2c3d4e5f6
Create Date: 2026-07-30 06:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "d2f7c3a9b1e4"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "apple_user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
            )
        )
        batch_op.create_index(
            batch_op.f("ix_user_apple_user_id"), ["apple_user_id"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_apple_user_id"))
        batch_op.drop_column("apple_user_id")
