"""empty message

Revision ID: 80c60bbccf1a
Revises: c8378de8fba5
Create Date: 2021-09-15 20:28:06.913193

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '80c60bbccf1a'
down_revision = 'c8378de8fba5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Transaction', 'ext_transaction_id',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Transaction', 'ext_transaction_id',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    # ### end Alembic commands ###