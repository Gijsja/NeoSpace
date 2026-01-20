"""Add index on profile_posts(created_at)

Revision ID: 3e83b4c19d45
Revises: f5888d5eac95
Create Date: 2026-01-20 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e83b4c19d45'
down_revision = 'f5888d5eac95'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE INDEX IF NOT EXISTS idx_posts_created ON profile_posts(created_at)")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_posts_created")
