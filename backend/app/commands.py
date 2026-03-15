from __future__ import annotations

import click
from sqlalchemy import or_, select

from app.extensions import db
from app.models import Paste, RefreshToken, User, UserRole
from app.utils.file_storage import delete_file_if_exists
from app.utils.time import now_utc


def register_commands(app) -> None:
    @app.cli.command("clean-expired")
    def clean_expired() -> None:
        """Delete expired and soft-deleted pastes."""
        now = now_utc()
        expired = db.session.scalars(
            select(Paste).where(or_(Paste.expires_at <= now, Paste.deleted_at.is_not(None)))
        ).all()

        deleted_count = 0
        for paste in expired:
            delete_file_if_exists(paste.file_path)
            db.session.delete(paste)
            deleted_count += 1

        stale_tokens = db.session.scalars(
            select(RefreshToken).where(
                or_(RefreshToken.expires_at <= now, RefreshToken.revoked.is_(True))
            )
        ).all()
        token_count = 0
        for token in stale_tokens:
            db.session.delete(token)
            token_count += 1

        db.session.commit()
        click.echo(f"Deleted {deleted_count} expired/deleted pastes")
        click.echo(f"Deleted {token_count} stale refresh tokens")

    @app.cli.command("make-admin")
    @click.argument("username")
    def make_admin(username: str) -> None:
        """Promote an existing user to admin role."""
        user = db.session.scalar(select(User).where(User.username == username))
        if user is None:
            raise click.ClickException("User not found")
        user.role = UserRole.ADMIN
        db.session.commit()
        click.echo(f"User '{username}' promoted to admin")
