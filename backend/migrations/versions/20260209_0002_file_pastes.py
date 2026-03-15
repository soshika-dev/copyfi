"""add file paste columns

Revision ID: 20260209_0002
Revises: 20260208_0001
Create Date: 2026-02-09 16:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260209_0002"
down_revision = "20260208_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pastes", sa.Column("is_file", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("pastes", sa.Column("file_name", sa.String(length=255), nullable=True))
    op.add_column("pastes", sa.Column("file_mime_type", sa.String(length=255), nullable=True))
    op.add_column("pastes", sa.Column("file_size", sa.Integer(), nullable=True))
    op.add_column("pastes", sa.Column("file_path", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("pastes", "file_path")
    op.drop_column("pastes", "file_size")
    op.drop_column("pastes", "file_mime_type")
    op.drop_column("pastes", "file_name")
    op.drop_column("pastes", "is_file")
