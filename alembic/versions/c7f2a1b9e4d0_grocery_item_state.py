"""grocery_item_state

Revision ID: c7f2a1b9e4d0
Revises: 4bd3eec5c064
Create Date: 2026-07-28 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import api


# revision identifiers, used by Alembic.
revision: str = "c7f2a1b9e4d0"
down_revision: Union[str, None] = "4bd3eec5c064"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "groceryitemstate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("item_key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("updated_on", api.core.timezone_handler.UTCDateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["user.id"],
            name=op.f("fk_groceryitemstate_created_by_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groceryitemstate")),
    )
    with op.batch_alter_table("groceryitemstate", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_groceryitemstate_id"), ["id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_groceryitemstate_created_by_id"),
            ["created_by_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_groceryitemstate_item_key"), ["item_key"], unique=False
        )
        batch_op.create_index(
            "ix_groceryitemstate_user_item_key",
            ["created_by_id", "item_key"],
            unique=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("groceryitemstate", schema=None) as batch_op:
        batch_op.drop_index("ix_groceryitemstate_user_item_key")
        batch_op.drop_index(batch_op.f("ix_groceryitemstate_item_key"))
        batch_op.drop_index(batch_op.f("ix_groceryitemstate_created_by_id"))
        batch_op.drop_index(batch_op.f("ix_groceryitemstate_id"))

    op.drop_table("groceryitemstate")
