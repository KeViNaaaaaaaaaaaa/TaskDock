"""Initial migration

Revision ID: 92551ad2391c
Revises: 00c67b7a5799
Create Date: 2024-11-13 12:03:33.868099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '92551ad2391c'
down_revision: Union[str, None] = '00c67b7a5799'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_unique_constraint("uq_users_nickname", ["nickname"])


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_nickname", type_="unique")
