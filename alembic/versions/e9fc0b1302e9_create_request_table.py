"""Create Request table

Revision ID: e9fc0b1302e9
Revises: 622509e4304d
Create Date: 2022-07-20 09:41:14.831514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9fc0b1302e9'
down_revision = '622509e4304d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'requests',
        sa.Column('id',           sa.Integer(),
                  nullable=False, primary_key=True),
        sa.Column('date_joined',  sa.sql.sqltypes.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.sql.expression.text('now()')),
        sa.Column('email',        sa.String(),
                  nullable=False, unique=True),
        sa.Column('description',  sa.String(),
                  nullable=False, server_default=''),
        sa.Column('client_id',    sa.Integer())
        )
    op.create_foreign_key('requests_clients_fk', source_table='requests', referent_table='clients',
                          local_cols=['client_id'], remote_cols=['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('requests_clients_fk', table_name="requests")
    op.drop_table('requests')
