"""Expanded acceptable phone numbers

Revision ID: 085e65b8c7f1
Revises: e9fc0b1302e9
Create Date: 2022-07-20 21:59:19.076620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '085e65b8c7f1'
down_revision = 'e9fc0b1302e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('clients', 'phone_number', type_=sa.types.String(length=22))


def downgrade() -> None:
    op.alter_column('clients', 'phone_number', type_=sa.types.String(length=10))
