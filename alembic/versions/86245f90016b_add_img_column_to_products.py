"""add img column to products

Revision ID: 86245f90016b
Revises: d2454f487cef
Create Date: 2026-04-21 14:21:08.089104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86245f90016b'
down_revision: Union[str, Sequence[str], None] = 'd2454f487cef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('product_img', sa.String(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('products', 'product_img')