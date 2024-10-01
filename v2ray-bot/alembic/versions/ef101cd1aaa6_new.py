"""new

Revision ID: ef101cd1aaa6
Revises: 085943943740
Create Date: 2024-10-01 15:43:01.732895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef101cd1aaa6'
down_revision: Union[str, None] = '085943943740'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
