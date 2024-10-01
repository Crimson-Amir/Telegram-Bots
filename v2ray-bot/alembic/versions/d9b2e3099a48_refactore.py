"""reFactore

Revision ID: d9b2e3099a48
Revises: ef101cd1aaa6
Create Date: 2024-10-02 00:55:44.934892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9b2e3099a48'
down_revision: Union[str, None] = 'ef101cd1aaa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
