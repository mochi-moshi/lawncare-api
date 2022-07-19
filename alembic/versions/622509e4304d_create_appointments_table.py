"""create_appointments_table

Revision ID: 622509e4304d
Revises: 7f7d9bf6f996
Create Date: 2022-07-19 08:15:15.630231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '622509e4304d'
down_revision = '7f7d9bf6f996'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'appointments',
        sa.Column('id',           sa.Integer(),
                  nullable=False, primary_key=True),
        sa.Column('date',  sa.sql.sqltypes.Date(),
                  nullable=False),
        sa.Column('client_id',    sa.Integer(),
                  nullable=False),
        sa.Column('description',  sa.String(),
                  nullable=False, server_default=''),
        sa.Column('price',        sa.Float(),
                  nullable=False),
        sa.Column('paid',         sa.sql.sqltypes.Boolean(),
                  nullable=False, server_default='f')
        )
    op.create_foreign_key('appointments_clients_fk', source_table='appointments', referent_table='clients',
                          local_cols=['client_id'], remote_cols=['id'], ondelete='CASCADE')

def downgrade() -> None:
    op.drop_constraint('appointments_clients_fk', table_name="appointments")
    op.drop_table('appointments')
