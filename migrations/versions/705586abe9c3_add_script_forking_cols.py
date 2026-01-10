"""add_script_forking_cols

Revision ID: 705586abe9c3
Revises: 2c93848123ab
Create Date: 2026-01-10 18:34:38.685486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '705586abe9c3'
down_revision: Union[str, None] = '2c93848123ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('scripts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('root_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_scripts_parent_id', 'scripts', ['parent_id'], ['id'])
        batch_op.create_foreign_key('fk_scripts_root_id', 'scripts', ['root_id'], ['id'])
        batch_op.create_index('idx_scripts_parent', ['parent_id'], unique=False)
        batch_op.create_index('idx_scripts_root', ['root_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('scripts', schema=None) as batch_op:
        batch_op.drop_index('idx_scripts_root')
        batch_op.drop_index('idx_scripts_parent')
        batch_op.drop_constraint('fk_scripts_root_id', type_='foreignkey')
        batch_op.drop_constraint('fk_scripts_parent_id', type_='foreignkey')
        batch_op.drop_column('root_id')
        batch_op.drop_column('parent_id')
