from __future__ import annotations

import uuid

from sqlalchemy import or_, select

from app.extensions import db
from app.models import Collection, Paste, PasteTag, PasteVisibility, User
from app.utils.errors import APIError
from app.utils.security import generate_slug, hash_secret, parse_expiration, verify_secret
from app.utils.time import now_utc


_MAX_SLUG_ATTEMPTS = 10


def ensure_content_size(content: str, max_bytes: int) -> None:
    size = len(content.encode("utf-8"))
    if size > max_bytes:
        raise APIError(
            "content_too_large",
            f"Paste content exceeds {max_bytes} bytes",
            413,
            details={"max_bytes": max_bytes, "actual_bytes": size},
        )


def make_unique_slug() -> str:
    for _ in range(_MAX_SLUG_ATTEMPTS):
        slug = generate_slug(10)
        exists = db.session.scalar(select(Paste.id).where(Paste.slug == slug))
        if not exists:
            return slug
    raise APIError("slug_generation_failed", "Could not generate unique slug", 500)


def get_active_paste_by_slug(slug: str) -> Paste | None:
    now = now_utc()
    query = select(Paste).where(
        Paste.slug == slug,
        Paste.deleted_at.is_(None),
        or_(Paste.expires_at.is_(None), Paste.expires_at > now),
    )
    return db.session.scalar(query)


def get_any_paste_by_slug(slug: str) -> Paste | None:
    return db.session.scalar(select(Paste).where(Paste.slug == slug, Paste.deleted_at.is_(None)))


def check_collection_owner(collection_id: uuid.UUID | None, owner_id: uuid.UUID | None) -> Collection | None:
    if collection_id is None:
        return None
    if owner_id is None:
        raise APIError("collection_requires_owner", "Anonymous users cannot use collections", 400)
    collection = db.session.get(Collection, collection_id)
    if collection is None or collection.owner_id != owner_id:
        raise APIError("collection_not_found", "Collection not found", 404)
    return collection


def apply_tags(paste: Paste, tags: list[str]) -> None:
    paste.tags.clear()
    for tag in tags:
        paste.tags.append(PasteTag(tag=tag))


def can_view_paste(paste: Paste, user: User | None) -> bool:
    if paste.visibility != PasteVisibility.PRIVATE:
        return True
    if user is None:
        return False
    return user.role.value == "admin" or paste.owner_id == user.id


def can_modify_paste(paste: Paste, user: User) -> bool:
    return user.role.value == "admin" or paste.owner_id == user.id


def requires_password(paste: Paste) -> bool:
    return bool(paste.password_hash)


def assert_paste_password(paste: Paste, provided_password: str | None) -> None:
    if not paste.password_hash:
        return
    if not provided_password:
        raise APIError("paste_password_required", "Paste password is required", 401)
    if not verify_secret(provided_password, paste.password_hash):
        raise APIError("invalid_paste_password", "Invalid paste password", 401)


def set_paste_password(paste: Paste, password: str | None) -> None:
    paste.password_hash = hash_secret(password) if password else None


def set_paste_expiration(paste: Paste, expires_in: str | None) -> None:
    if expires_in is None:
        return
    try:
        paste.expires_at = parse_expiration(expires_in)
    except ValueError as exc:
        raise APIError("invalid_expiration", "Invalid expiration value", 422) from exc


def increment_view_or_burn(paste: Paste) -> None:
    paste.view_count += 1
    if paste.burn_after_read:
        paste.deleted_at = now_utc()


def serialize_paste(paste: Paste, include_content: bool = True) -> dict:
    payload = {
        "id": str(paste.id),
        "slug": paste.slug,
        "owner_id": str(paste.owner_id) if paste.owner_id else None,
        "collection_id": str(paste.collection_id) if paste.collection_id else None,
        "title": paste.title,
        "is_file": paste.is_file,
        "file_name": paste.file_name,
        "file_mime_type": paste.file_mime_type,
        "file_size": paste.file_size,
        "language": paste.language,
        "visibility": paste.visibility.value,
        "expires_at": paste.expires_at.isoformat() if paste.expires_at else None,
        "burn_after_read": paste.burn_after_read,
        "view_count": paste.view_count,
        "is_password_protected": bool(paste.password_hash),
        "tags": [tag.tag for tag in paste.tags],
        "created_at": paste.created_at.isoformat(),
        "updated_at": paste.updated_at.isoformat(),
    }
    if include_content:
        payload["content"] = None if paste.is_file else paste.content
    if paste.is_file:
        payload["download_url"] = f"/api/v1/pastes/{paste.slug}/download"
    return payload
