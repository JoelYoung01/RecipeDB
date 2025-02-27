"""file_uploads

Revision ID: 4bd3eec5c064
Revises: 5455f6981941
Create Date: 2025-02-27 13:37:48.819810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import api


# revision identifiers, used by Alembic.
revision: str = '4bd3eec5c064'
down_revision: Union[str, None] = '5455f6981941'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cover_image_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_recipe_cover_image_id_upload'), 'upload', ['cover_image_id'], ['id'])

    with op.batch_alter_table('upload', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('upload', schema=None) as batch_op:
        batch_op.drop_column('name')

    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_recipe_cover_image_id_upload'), type_='foreignkey')
        batch_op.drop_column('cover_image_id')

    # ### end Alembic commands ###
