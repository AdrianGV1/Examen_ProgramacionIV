"""add radiograph image visibility fields

Revision ID: 3f7e9a1b2c4d
Revises: c99537b981e9
Create Date: 2026-04-18 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f7e9a1b2c4d"
down_revision = "c99537b981e9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("radiographs", sa.Column("image_public_id", sa.String(length=255), nullable=True))
    op.add_column(
        "radiographs",
        sa.Column("image_is_private", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("radiographs", sa.Column("image_hidden_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("radiographs", "image_hidden_at")
    op.drop_column("radiographs", "image_is_private")
    op.drop_column("radiographs", "image_public_id")
