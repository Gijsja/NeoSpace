"""add feed index

Revision ID: a1b2c3d4e5f6
Revises: c04b1fbdddc9
Create Date: 2026-01-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'c04b1fbdddc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create composite index to optimize feed queries (ORDER BY created_at)
    # This enables Deferred Row Loading when sorting by created_at
    # for a specific profile
    op.create_index(
        'idx_posts_profile_created',
        'profile_posts',
        ['profile_id', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_posts_profile_created', table_name='profile_posts')
