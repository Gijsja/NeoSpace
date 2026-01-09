"""add_cat_personalities_and_bot_columns

Revision ID: 8f84ce0eef2a
Revises: 0aa9fe16b483
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f84ce0eef2a'
down_revision = '0aa9fe16b483'
branch_labels = None
depends_on = None


def upgrade():
    # Create cat_personalities table first
    op.execute('''
        CREATE TABLE IF NOT EXISTS cat_personalities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            priority INTEGER DEFAULT 5,
            triggers TEXT,              -- JSON array of event triggers
            mode TEXT DEFAULT 'cute',   -- 'cute', 'pirate', 'formal'
            silence_bias REAL DEFAULT 0.5,
            global_observer INTEGER DEFAULT 0,
            pleasure_weight REAL DEFAULT 1.0,
            arousal_weight REAL DEFAULT 0.5,
            dominance_weight REAL DEFAULT 1.0,
            dialogues TEXT,             -- JSON dialogue templates
            avatar_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Add is_bot column to users (batch mode for SQLite)
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('is_bot', sa.Boolean(), server_default='0'))
        batch_op.add_column(sa.Column('bot_personality_id', sa.Integer(), nullable=True))
    
    # Create index for bot users
    op.execute('CREATE INDEX IF NOT EXISTS idx_users_is_bot ON users(is_bot);')


def downgrade():
    # Remove bot columns from users
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('bot_personality_id')
        batch_op.drop_column('is_bot')
    
    # Drop cat_personalities table
    op.execute('DROP TABLE IF EXISTS cat_personalities;')
    op.execute('DROP INDEX IF EXISTS idx_users_is_bot;')
