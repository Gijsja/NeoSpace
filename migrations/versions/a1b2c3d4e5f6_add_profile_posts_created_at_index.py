"""add_profile_posts_created_at_index

Revision ID: a1b2c3d4e5f6
Revises: 705586abe9c3
Create Date: 2026-01-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '705586abe9c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('profile_posts', schema=None) as batch_op:
        batch_op.create_index(
            'idx_posts_profile_created',
            ['profile_id', 'created_at'],
            unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table('profile_posts', schema=None) as batch_op:
        batch_op.drop_index('idx_posts_profile_created')
