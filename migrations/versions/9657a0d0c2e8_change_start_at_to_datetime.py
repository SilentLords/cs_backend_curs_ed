"""Change start_at to datetime

Revision ID: 9657a0d0c2e8
Revises: 0048f137583b
Create Date: 2023-12-14 10:21:37.043581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9657a0d0c2e8'
down_revision: Union[str, None] = '0048f137583b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('gift_events', 'start_at',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('gift_events', 'start_at',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    # ### end Alembic commands ###
