from __future__ import annotations

import uuid
from datetime import timedelta

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended.utils import get_jti
from sqlalchemy import or_, select

from app.extensions import db
from app.models import RefreshToken, User, UserRole
from app.utils.errors import APIError
from app.utils.security import hash_secret, verify_secret
from app.utils.time import now_utc


def _find_user_by_username_or_email(username: str) -> User | None:
    return db.session.scalar(
        select(User).where(or_(User.username == username, User.email == username))
    )


def create_user(username: str, password: str, email: str | None = None) -> User:
    existing_user = db.session.scalar(select(User).where(User.username == username))
    if existing_user:
        raise APIError("username_taken", "Username is already in use", 409)

    if email:
        existing_email = db.session.scalar(select(User).where(User.email == email))
        if existing_email:
            raise APIError("email_taken", "Email is already in use", 409)

    user = User(
        username=username,
        email=email,
        password_hash=hash_secret(password),
        role=UserRole.USER,
        is_active=True,
        is_banned=False,
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(username: str, password: str) -> User:
    user = _find_user_by_username_or_email(username)
    if user is None or not verify_secret(password, user.password_hash):
        raise APIError("invalid_credentials", "Invalid username or password", 401)
    if not user.is_active:
        raise APIError("inactive_account", "Account is inactive", 403)
    if user.is_banned:
        raise APIError("banned_account", "Account is banned", 403)
    user.last_login_at = now_utc()
    db.session.commit()
    return user


def _persist_refresh_token(user: User, refresh_token: str) -> None:
    jti = get_jti(refresh_token)
    refresh_expires: timedelta = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    record = RefreshToken(
        user_id=user.id,
        jti=jti,
        expires_at=now_utc() + refresh_expires,
        revoked=False,
        created_at=now_utc(),
    )
    db.session.add(record)


def issue_tokens(user: User) -> dict[str, str]:
    claims = {"role": user.role.value, "username": user.username}
    access_token = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)
    _persist_refresh_token(user, refresh_token)
    db.session.commit()
    return {"access_token": access_token, "refresh_token": refresh_token}


def rotate_refresh_token(user: User, current_jti: str) -> dict[str, str]:
    revoke_refresh_token(current_jti)
    return issue_tokens(user)


def revoke_refresh_token(jti: str) -> None:
    token = db.session.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if token is None:
        return
    token.revoked = True
    db.session.commit()


def is_refresh_token_revoked(jti: str) -> bool:
    token = db.session.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if token is None:
        return True
    if token.revoked:
        return True
    if token.expires_at <= now_utc():
        return True
    return False


def get_user_by_identity(identity: str | None) -> User | None:
    if identity is None:
        return None
    try:
        user_id = uuid.UUID(identity)
    except ValueError:
        return None
    return db.session.get(User, user_id)


def require_active_user(identity: str | None) -> User:
    user = get_user_by_identity(identity)
    if user is None:
        raise APIError("user_not_found", "User not found", 401)
    if not user.is_active:
        raise APIError("inactive_account", "Account is inactive", 403)
    if user.is_banned:
        raise APIError("banned_account", "Account is banned", 403)
    return user
