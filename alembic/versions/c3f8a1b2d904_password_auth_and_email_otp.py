"""password_auth_and_email_otp

Revision ID: c3f8a1b2d904
Revises: 4bd3eec5c064
Create Date: 2026-07-28 01:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import api


# revision identifiers, used by Alembic.
revision: str = "c3f8a1b2d904"
down_revision: Union[str, None] = "4bd3eec5c064"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "email_verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=True
            )
        )
        batch_op.create_index(batch_op.f("ix_user_email"), ["email"], unique=True)
        batch_op.create_index(
            batch_op.f("ix_user_google_user_id"), ["google_user_id"], unique=False
        )

    # Existing rows were Google / seeded accounts — treat as verified.
    op.execute(sa.text("UPDATE user SET email_verified = 1"))

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("email_verified", server_default=None)

    op.create_table(
        "emailverificationchallenge",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("otp_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("expires_at", api.core.timezone_handler.UTCDateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column(
            "last_sent_at", api.core.timezone_handler.UTCDateTime(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_emailverificationchallenge_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_emailverificationchallenge")),
        sa.UniqueConstraint(
            "user_id", name=op.f("uq_emailverificationchallenge_user_id")
        ),
    )
    with op.batch_alter_table("emailverificationchallenge", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_emailverificationchallenge_id"), ["id"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("emailverificationchallenge", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_emailverificationchallenge_id"))
    op.drop_table("emailverificationchallenge")

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_google_user_id"))
        batch_op.drop_index(batch_op.f("ix_user_email"))
        batch_op.drop_column("hashed_password")
        batch_op.drop_column("email_verified")
