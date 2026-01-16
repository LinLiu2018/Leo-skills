"""
Create Lead table

Revision ID: 20260114142513
Create Date: 2026-01-14T14:25:13.634889
"""
from alembic import op
import sqlalchemy as sa

revision = '20260114142513'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(255), nullable=True),
        sa.Column('depth', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 创建索引
    op.create_index('ix_leads_status', 'leads', ['status'])
    op.create_index('ix_leads_phone', 'leads', ['phone'])


def downgrade():
    op.drop_table('leads')
