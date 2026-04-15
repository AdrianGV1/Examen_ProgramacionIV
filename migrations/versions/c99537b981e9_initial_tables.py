"""initial tables

Revision ID: c99537b981e9
Revises: 
Create Date: 2026-04-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c99537b981e9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		"users",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column("email", sa.String(length=255), nullable=False),
		sa.Column("name", sa.String(length=150), nullable=False),
		sa.Column("picture", sa.String(length=500), nullable=True),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.Column("updated_at", sa.DateTime(), nullable=False),
		sa.UniqueConstraint("email"),
	)

	op.create_table(
		"radiographs",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column("patient_name", sa.String(length=255), nullable=False),
		sa.Column("patient_id_number", sa.String(length=100), nullable=False),
		sa.Column("clinical_reference", sa.String(length=255), nullable=False),
		sa.Column("study_date", sa.Date(), nullable=False),
		sa.Column("image_url", sa.String(length=500), nullable=True),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.Column("updated_at", sa.DateTime(), nullable=False),
	)


def downgrade() -> None:
	op.drop_table("radiographs")
	op.drop_table("users")
