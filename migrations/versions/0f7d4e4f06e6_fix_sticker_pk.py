"""fix_sticker_pk

Revision ID: 0f7d4e4f06e6
Revises: 1b811fd21d41
Create Date: 2026-01-09 00:33:59.036900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f7d4e4f06e6'
down_revision: Union[str, None] = '1b811fd21d41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix profile_stickers ID type (Integer -> Text)
    # Using batch mode to support SQLite table recreation
    with op.batch_alter_table('profile_stickers', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.Text(),
               nullable=False)
        # Type changes for float columns, ensuring they are floats
        batch_op.alter_column('x_pos',
               existing_type=sa.REAL(),
               type_=sa.Float(),
               existing_nullable=False)
        batch_op.alter_column('y_pos',
               existing_type=sa.REAL(),
               type_=sa.Float(),
               existing_nullable=False)
        batch_op.alter_column('rotation',
               existing_type=sa.REAL(),
               type_=sa.Float(),
               existing_nullable=True,
               existing_server_default=sa.text('0'))
        batch_op.alter_column('scale',
               existing_type=sa.REAL(),
               type_=sa.Float(),
               existing_nullable=True,
               existing_server_default=sa.text('1'))
        # NOTE: Removed drop/create constraint to avoid Unnamed Constraint error.
        # Batch mode should preserve existing FKs.


def downgrade() -> None:
    with op.batch_alter_table('profile_stickers', schema=None) as batch_op:
        batch_op.alter_column('scale',
               existing_type=sa.Float(),
               type_=sa.REAL(),
               existing_nullable=True,
               existing_server_default=sa.text('1'))
        batch_op.alter_column('rotation',
               existing_type=sa.Float(),
               type_=sa.REAL(),
               existing_nullable=True,
               existing_server_default=sa.text('0'))
        batch_op.alter_column('y_pos',
               existing_type=sa.Float(),
               type_=sa.REAL(),
               existing_nullable=False)
        batch_op.alter_column('x_pos',
               existing_type=sa.Float(),
               type_=sa.REAL(),
               existing_nullable=False)
        batch_op.alter_column('id',
               existing_type=sa.Text(),
               type_=sa.INTEGER(),
               nullable=True)
