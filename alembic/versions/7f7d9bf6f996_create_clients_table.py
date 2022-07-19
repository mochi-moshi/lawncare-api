"""Create Clients Table

Revision ID: 7f7d9bf6f996
Revises: 
Create Date: 2022-07-19 02:14:17.259018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f7d9bf6f996'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'clients',
        sa.Column('id',           sa.Integer(),
                  nullable=False, primary_key=True),
        sa.Column('date_joined',  sa.sql.sqltypes.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.sql.expression.text('now()')),
        sa.Column('name',         sa.String(),
                  nullable=False),
        sa.Column('email',        sa.String(),
                  nullable=False, unique=True),
        sa.Column('phone_number', sa.String(length=10),
                  nullable=False),
        sa.Column('password',     sa.String(),
                  nullable=False),
        sa.Column('address',      sa.String(),
                  nullable=False)
        )


def downgrade() -> None:
    op.drop_table('clients')