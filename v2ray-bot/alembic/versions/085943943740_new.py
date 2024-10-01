"""new

Revision ID: 085943943740
Revises: f861f6768de6
Create Date: 2024-10-01 15:42:05.026728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '085943943740'
down_revision: Union[str, None] = 'f861f6768de6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
