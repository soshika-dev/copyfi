"""initial schema

Revision ID: 20260208_0001
Revises:
Create Date: 2026-02-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260208_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("user", "admin", name="userrole", native_enum=False), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "collections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name=op.f("fk_collections_owner_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_collections")),
        sa.UniqueConstraint("owner_id", "name", name="uq_collections_owner_name"),
    )
    op.create_index(op.f("ix_collections_owner_id"), "collections", ["owner_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_refresh_tokens_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
    )
    op.create_index(op.f("ix_refresh_tokens_jti"), "refresh_tokens", ["jti"], unique=True)
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_revoked"), "refresh_tokens", ["revoked"], unique=False)

    op.create_table(
        "pastes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=16), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column("collection_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column(
            "visibility",
            sa.Enum("public", "unlisted", "private", name="pastevisibility", native_enum=False),
            nullable=False,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("burn_after_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="SET NULL", name=op.f("fk_pastes_collection_id_collections")),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_pastes_owner_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pastes")),
    )
    op.create_index(op.f("ix_pastes_slug"), "pastes", ["slug"], unique=True)
    op.create_index(op.f("ix_pastes_owner_id"), "pastes", ["owner_id"], unique=False)
    op.create_index(op.f("ix_pastes_collection_id"), "pastes", ["collection_id"], unique=False)
    op.create_index(op.f("ix_pastes_expires_at"), "pastes", ["expires_at"], unique=False)
    op.create_index(op.f("ix_pastes_deleted_at"), "pastes", ["deleted_at"], unique=False)
    op.create_index("ix_pastes_owner_visibility", "pastes", ["owner_id", "visibility"], unique=False)

    op.create_table(
        "paste_tags",
        sa.Column("paste_id", sa.Uuid(), nullable=False),
        sa.Column("tag", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["paste_id"], ["pastes.id"], ondelete="CASCADE", name=op.f("fk_paste_tags_paste_id_pastes")),
        sa.PrimaryKeyConstraint("paste_id", "tag", name=op.f("pk_paste_tags")),
    )
    op.create_index(op.f("ix_paste_tags_tag"), "paste_tags", ["tag"], unique=False)

    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("paste_id", sa.Uuid(), nullable=False),
        sa.Column("reporter_user_id", sa.Uuid(), nullable=True),
        sa.Column("reporter_ip", sa.String(length=45), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("open", "reviewed", "actioned", name="reportstatus", native_enum=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["paste_id"], ["pastes.id"], ondelete="CASCADE", name=op.f("fk_reports_paste_id_pastes")),
        sa.ForeignKeyConstraint(["reporter_user_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_reports_reporter_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reports")),
    )
    op.create_index(op.f("ix_reports_paste_id"), "reports", ["paste_id"], unique=False)
    op.create_index(op.f("ix_reports_reporter_user_id"), "reports", ["reporter_user_id"], unique=False)
    op.create_index(op.f("ix_reports_status"), "reports", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reports_status"), table_name="reports")
    op.drop_index(op.f("ix_reports_reporter_user_id"), table_name="reports")
    op.drop_index(op.f("ix_reports_paste_id"), table_name="reports")
    op.drop_table("reports")

    op.drop_index(op.f("ix_paste_tags_tag"), table_name="paste_tags")
    op.drop_table("paste_tags")

    op.drop_index("ix_pastes_owner_visibility", table_name="pastes")
    op.drop_index(op.f("ix_pastes_deleted_at"), table_name="pastes")
    op.drop_index(op.f("ix_pastes_expires_at"), table_name="pastes")
    op.drop_index(op.f("ix_pastes_collection_id"), table_name="pastes")
    op.drop_index(op.f("ix_pastes_owner_id"), table_name="pastes")
    op.drop_index(op.f("ix_pastes_slug"), table_name="pastes")
    op.drop_table("pastes")

    op.drop_index(op.f("ix_refresh_tokens_revoked"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_jti"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index(op.f("ix_collections_owner_id"), table_name="collections")
    op.drop_table("collections")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
