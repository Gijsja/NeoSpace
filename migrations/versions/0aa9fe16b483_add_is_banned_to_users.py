"""add_is_banned_to_users

Revision ID: 0aa9fe16b483
Revises: f5888d5eac95
Create Date: 2026-01-09 01:11:53.297689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0aa9fe16b483'
down_revision: Union[str, None] = 'f5888d5eac95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_banned', sa.Integer(), server_default='0'))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_banned')
