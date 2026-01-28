"""
Create Reward table

Revision ID: 20260114143622
Create Date: 2026-01-14T14:36:22.714202
"""
from alembic import op
import sqlalchemy as sa

revision = '20260114143622'
down_revision = '20260114143555'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rewards',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('reward_type', sa.String(20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 创建索引
    op.create_index('ix_rewards_lead_id', 'rewards', ['lead_id'])
    op.create_index('ix_rewards_status', 'rewards', ['status'])


def downgrade():
    op.drop_table('rewards')
