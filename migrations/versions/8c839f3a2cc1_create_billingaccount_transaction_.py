"""Create BillingAccount, Transaction, TransactionBlock

Revision ID: 8c839f3a2cc1
Revises: 3619e4d0ef44
Create Date: 2023-11-16 15:43:35.829311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c839f3a2cc1'
down_revision: Union[str, None] = '3619e4d0ef44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('billing_account',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('balance', sa.Float(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_billing_account_id'), 'billing_account', ['id'], unique=False)
    op.create_table('transaction',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('account_id', sa.Integer(), nullable=True),
                    sa.Column('amount', sa.Float(), nullable=False),
                    sa.Column('balance_after_transaction', sa.Float(), nullable=False),
                    sa.Column('type', sa.String(length=255), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                    sa.ForeignKeyConstraint(['account_id'], ['billing_account.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_transaction_id'), 'transaction', ['id'], unique=False)
    op.create_table('transaction_block',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('transaction_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                    sa.ForeignKeyConstraint(['transaction_id'], ['transaction.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_transaction_block_id'), 'transaction_block', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_block_id'), table_name='transaction_block')
    op.drop_table('transaction_block')
    op.drop_index(op.f('ix_transaction_id'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_billing_account_id'), table_name='billing_account')
    op.drop_table('billing_account')
    # ### end Alembic commands ###
