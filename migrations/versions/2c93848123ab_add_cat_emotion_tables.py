"""Add cat emotional intelligence tables

Revision ID: 2c93848123ab
Revises: 8f84ce0eef2a
Create Date: 2026-01-10 12:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision = '2c93848123ab'
down_revision = '8f84ce0eef2a'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Create cat_factions
    op.create_table(
        'cat_factions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('traits', sa.Text(), nullable=True), # Stored as JSON string
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create cat_states
    op.create_table(
        'cat_states',
        sa.Column('cat_id', sa.Integer(), nullable=False),
        sa.Column('pleasure', sa.Float(), nullable=True),
        sa.Column('arousal', sa.Float(), nullable=True),
        sa.Column('dominance', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['cat_id'], ['cat_personalities.id'], ),
        sa.PrimaryKeyConstraint('cat_id')
    )

    # 3. Add column to cat_personalities
    # SQLite has limited ALTER TABLE support, but Alembic usually handles add_column fine
    with op.batch_alter_table('cat_personalities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('faction_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_cat_personalities_faction_id', 'cat_factions', ['faction_id'], ['id'])

def downgrade():
    with op.batch_alter_table('cat_personalities', schema=None) as batch_op:
        batch_op.drop_constraint('fk_cat_personalities_faction_id', type_='foreignkey')
        batch_op.drop_column('faction_id')

    op.drop_table('cat_states')
    op.drop_table('cat_factions')
