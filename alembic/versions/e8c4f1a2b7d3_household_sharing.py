"""household sharing

Revision ID: e8c4f1a2b7d3
Revises: d2f7c3a9b1e4
Create Date: 2026-08-05 18:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

import api

# revision identifiers, used by Alembic.
revision: str = "e8c4f1a2b7d3"
down_revision: Union[str, None] = "d2f7c3a9b1e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "household",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_on", api.core.timezone_handler.UTCDateTime(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["user.id"],
            name=op.f("fk_household_created_by_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_household")),
    )
    with op.batch_alter_table("household", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_household_id"), ["id"], unique=False)

    op.create_table(
        "householdmember",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("household_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "joined_on", api.core.timezone_handler.UTCDateTime(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["household.id"],
            name=op.f("fk_householdmember_household_id_household"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_householdmember_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_householdmember")),
        sa.UniqueConstraint(
            "user_id", name=op.f("uq_householdmember_user_id")
        ),
    )
    with op.batch_alter_table("householdmember", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_householdmember_id"), ["id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_householdmember_household_id"),
            ["household_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_householdmember_user_id"), ["user_id"], unique=False
        )

    op.create_table(
        "householdinvite",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("household_id", sa.Integer(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("invited_by_id", sa.Integer(), nullable=False),
        sa.Column("token", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "created_on", api.core.timezone_handler.UTCDateTime(), nullable=False
        ),
        sa.Column(
            "expires_on", api.core.timezone_handler.UTCDateTime(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["household.id"],
            name=op.f("fk_householdinvite_household_id_household"),
        ),
        sa.ForeignKeyConstraint(
            ["invited_by_id"],
            ["user.id"],
            name=op.f("fk_householdinvite_invited_by_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_householdinvite")),
        sa.UniqueConstraint("token", name=op.f("uq_householdinvite_token")),
    )
    with op.batch_alter_table("householdinvite", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_householdinvite_id"), ["id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_householdinvite_household_id"),
            ["household_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_householdinvite_email"), ["email"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_householdinvite_token"), ["token"], unique=False
        )

    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.add_column(sa.Column("household_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_recipe_household_id"), ["household_id"], unique=False
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_recipe_household_id_household"),
            "household",
            ["household_id"],
            ["id"],
        )

    with op.batch_alter_table("plannedrecipe", schema=None) as batch_op:
        batch_op.add_column(sa.Column("household_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_plannedrecipe_household_id"),
            ["household_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_plannedrecipe_household_id_household"),
            "household",
            ["household_id"],
            ["id"],
        )

    with op.batch_alter_table("groceryitemstate", schema=None) as batch_op:
        batch_op.add_column(sa.Column("household_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_groceryitemstate_household_id"),
            ["household_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_groceryitemstate_household_id_household"),
            "household",
            ["household_id"],
            ["id"],
        )

    # Backfill: one solo household per user, attach their rows.
    conn = op.get_bind()
    users = conn.execute(sa.text("SELECT id, display_name FROM user")).fetchall()
    for user_id, display_name in users:
        name = f"{(display_name or 'My').strip() or 'My'}'s kitchen"
        conn.execute(
            sa.text(
                "INSERT INTO household (name, created_by_id, created_on) "
                "VALUES (:name, :uid, CURRENT_TIMESTAMP)"
            ),
            {"name": name, "uid": user_id},
        )
        household_id = conn.execute(sa.text("SELECT last_insert_rowid()")).scalar()
        conn.execute(
            sa.text(
                "INSERT INTO householdmember "
                "(household_id, user_id, role, joined_on) "
                "VALUES (:hid, :uid, 'owner', CURRENT_TIMESTAMP)"
            ),
            {"hid": household_id, "uid": user_id},
        )
        conn.execute(
            sa.text(
                "UPDATE recipe SET household_id = :hid WHERE created_by_id = :uid"
            ),
            {"hid": household_id, "uid": user_id},
        )
        conn.execute(
            sa.text(
                "UPDATE plannedrecipe SET household_id = :hid "
                "WHERE created_by_id = :uid"
            ),
            {"hid": household_id, "uid": user_id},
        )
        conn.execute(
            sa.text(
                "UPDATE groceryitemstate SET household_id = :hid "
                "WHERE created_by_id = :uid"
            ),
            {"hid": household_id, "uid": user_id},
        )

    # Any remaining nulls (shouldn't happen) get a fallback household from creator.
    # Make columns non-nullable.
    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.alter_column("household_id", existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table("plannedrecipe", schema=None) as batch_op:
        batch_op.alter_column("household_id", existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table("groceryitemstate", schema=None) as batch_op:
        batch_op.alter_column("household_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_index("ix_groceryitemstate_user_item_key")
        batch_op.create_index(
            "ix_groceryitemstate_household_item_key",
            ["household_id", "item_key"],
            unique=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("groceryitemstate", schema=None) as batch_op:
        batch_op.drop_index("ix_groceryitemstate_household_item_key")
        batch_op.create_index(
            "ix_groceryitemstate_user_item_key",
            ["created_by_id", "item_key"],
            unique=True,
        )
        batch_op.drop_constraint(
            batch_op.f("fk_groceryitemstate_household_id_household"),
            type_="foreignkey",
        )
        batch_op.drop_index(batch_op.f("ix_groceryitemstate_household_id"))
        batch_op.drop_column("household_id")

    with op.batch_alter_table("plannedrecipe", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_plannedrecipe_household_id_household"),
            type_="foreignkey",
        )
        batch_op.drop_index(batch_op.f("ix_plannedrecipe_household_id"))
        batch_op.drop_column("household_id")

    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_recipe_household_id_household"), type_="foreignkey"
        )
        batch_op.drop_index(batch_op.f("ix_recipe_household_id"))
        batch_op.drop_column("household_id")

    with op.batch_alter_table("householdinvite", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_householdinvite_token"))
        batch_op.drop_index(batch_op.f("ix_householdinvite_email"))
        batch_op.drop_index(batch_op.f("ix_householdinvite_household_id"))
        batch_op.drop_index(batch_op.f("ix_householdinvite_id"))
    op.drop_table("householdinvite")

    with op.batch_alter_table("householdmember", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_householdmember_user_id"))
        batch_op.drop_index(batch_op.f("ix_householdmember_household_id"))
        batch_op.drop_index(batch_op.f("ix_householdmember_id"))
    op.drop_table("householdmember")

    with op.batch_alter_table("household", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_household_id"))
    op.drop_table("household")
