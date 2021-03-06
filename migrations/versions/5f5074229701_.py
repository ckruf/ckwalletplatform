"""empty message

Revision ID: 5f5074229701
Revises: 
Create Date: 2021-09-07 17:51:19.753322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f5074229701'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('C_Transaction',
    sa.Column('c_transaction_id', sa.Integer(), nullable=False),
    sa.Column('transaction_type', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('c_transaction_id'),
    sa.UniqueConstraint('transaction_type')
    )
    op.create_table('Game',
    sa.Column('game_id', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('game_id')
    )
    op.create_table('Player',
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('nickname', sa.String(length=50), nullable=True),
    sa.Column('country', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('player_id')
    )
    op.create_table('Session',
    sa.Column('session_id', sa.String(length=50), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['Game.game_id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['Player.player_id'], ),
    sa.PrimaryKeyConstraint('session_id')
    )
    op.create_table('Wallet',
    sa.Column('wallet_id', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['player_id'], ['Player.player_id'], ),
    sa.PrimaryKeyConstraint('wallet_id')
    )
    op.create_table('Round',
    sa.Column('round_id', sa.String(length=50), nullable=False),
    sa.Column('session_id', sa.String(length=50), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['Session.session_id'], ),
    sa.PrimaryKeyConstraint('round_id')
    )
    op.create_table('Transaction',
    sa.Column('transaction_id', sa.String(length=50), nullable=False),
    sa.Column('transaction_type', sa.Integer(), nullable=False),
    sa.Column('wallet_id', sa.Integer(), nullable=False),
    sa.Column('amount_real', sa.Integer(), nullable=False),
    sa.Column('amount_bonus', sa.Integer(), nullable=False),
    sa.Column('occured_at', sa.DateTime(), nullable=False),
    sa.Column('ext_transaction_id', sa.String(length=50), nullable=False),
    sa.Column('round_id', sa.String(length=50), nullable=True),
    sa.Column('session_id', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['round_id'], ['Round.round_id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['Session.session_id'], ),
    sa.ForeignKeyConstraint(['transaction_type'], ['C_Transaction.c_transaction_id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['Wallet.wallet_id'], ),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Transaction')
    op.drop_table('Round')
    op.drop_table('Wallet')
    op.drop_table('Session')
    op.drop_table('Player')
    op.drop_table('Game')
    op.drop_table('C_Transaction')
    # ### end Alembic commands ###
