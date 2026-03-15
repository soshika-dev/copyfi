from __future__ import annotations

from pathlib import Path

from flask import Blueprint, Response, current_app, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from sqlalchemy import desc, func, or_, select

from app.extensions import db, limiter
from app.models import Paste, PasteVisibility, Report, ReportStatus
from app.schemas.common import parse_pagination
from app.schemas.paste import CreatePasteSchema, ReportSchema, UpdatePasteSchema
from app.services.auth_service import get_user_by_identity, require_active_user
from app.services.paste_service import (
    apply_tags,
    can_modify_paste,
    can_view_paste,
    check_collection_owner,
    ensure_content_size,
    get_active_paste_by_slug,
    get_any_paste_by_slug,
    increment_view_or_burn,
    make_unique_slug,
    serialize_paste,
    set_paste_expiration,
    set_paste_password,
)
from app.utils.errors import APIError
from app.utils.file_storage import delete_file_if_exists, save_upload
from app.utils.responses import json_response
from app.utils.time import now_utc

pastes_bp = Blueprint("pastes_v1", __name__, url_prefix="/pastes")


def _optional_user():
    verify_jwt_in_request(optional=True)
    return get_user_by_identity(get_jwt_identity())


@pastes_bp.get("/recent")
def recent_public_pastes():
    pagination = parse_pagination(request.args)
    page, limit = pagination.page, pagination.limit

    now = now_utc()
    base_query = select(Paste).where(
        Paste.visibility == PasteVisibility.PUBLIC,
        Paste.password_hash.is_(None),
        Paste.deleted_at.is_(None),
        or_(Paste.expires_at.is_(None), Paste.expires_at > now),
    )

    total = db.session.scalar(select(func.count()).select_from(base_query.subquery()))
    items = db.session.scalars(
        base_query.order_by(desc(Paste.created_at)).offset((page - 1) * limit).limit(limit)
    ).all()

    return json_response(
        {
            "data": [serialize_paste(item, include_content=False) for item in items],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": int(total or 0),
                "pages": (int(total or 0) + limit - 1) // limit,
            },
        }
    )


@pastes_bp.post("")
@limiter.limit("30 per hour")
def create_paste():
    user = _optional_user()
    if user is not None and (user.is_banned or not user.is_active):
        raise APIError("forbidden", "User cannot create pastes", 403)

    payload = CreatePasteSchema.model_validate(request.get_json(silent=False) or {})
    if payload.visibility == PasteVisibility.PRIVATE.value and user is None:
        raise APIError("auth_required", "Authentication required for private pastes", 401)

    ensure_content_size(payload.content, current_app.config["MAX_PASTE_BYTES"])
    owner_id = user.id if user else None
    check_collection_owner(payload.collection_id, owner_id)

    paste = Paste(
        slug=make_unique_slug(),
        owner_id=owner_id,
        collection_id=payload.collection_id,
        title=payload.title,
        content=payload.content,
        language=payload.language,
        visibility=PasteVisibility(payload.visibility),
        burn_after_read=payload.burn_after_read,
        view_count=0,
    )
    set_paste_expiration(paste, payload.expires_in)
    if payload.password:
        set_paste_password(paste, payload.password)
    apply_tags(paste, payload.tags)

    db.session.add(paste)
    db.session.commit()
    return json_response({"data": serialize_paste(paste)}, 201)


@pastes_bp.post("/file")
@limiter.limit("20 per hour")
def create_file_paste():
    user = _optional_user()
    if user is not None and (user.is_banned or not user.is_active):
        raise APIError("forbidden", "User cannot create pastes", 403)

    file_obj = request.files.get("file")
    visibility = (request.form.get("visibility") or "unlisted").strip().lower()
    if visibility not in {"public", "unlisted", "private"}:
        raise APIError("validation_error", "Invalid visibility", 422)
    if visibility == PasteVisibility.PRIVATE.value and user is None:
        raise APIError("auth_required", "Authentication required for private pastes", 401)

    owner_id = user.id if user else None
    collection_id = request.form.get("collection_id")
    if collection_id:
        import uuid

        try:
            parsed_collection = uuid.UUID(collection_id)
        except ValueError as exc:
            raise APIError("validation_error", "Invalid collection_id", 422) from exc
        check_collection_owner(parsed_collection, owner_id)
    else:
        parsed_collection = None

    file_path, file_name, file_mime, file_size = save_upload(file_obj)
    expires_in = request.form.get("expires_in", "never")
    password = request.form.get("password")
    burn_after_read = (request.form.get("burn_after_read", "false").strip().lower() == "true")
    title = request.form.get("title") or file_name

    paste = Paste(
        slug=make_unique_slug(),
        owner_id=owner_id,
        collection_id=parsed_collection,
        title=title[:200],
        content="",
        is_file=True,
        file_name=file_name,
        file_mime_type=file_mime,
        file_size=file_size,
        file_path=file_path,
        language=None,
        visibility=PasteVisibility(visibility),
        burn_after_read=burn_after_read,
        view_count=0,
    )
    set_paste_expiration(paste, expires_in)
    if password:
        set_paste_password(paste, password)

    tags_raw = request.form.get("tags", "")
    tags = sorted({tag.strip().lower() for tag in tags_raw.split(",") if tag.strip()})
    apply_tags(paste, tags[:20])

    db.session.add(paste)
    db.session.commit()
    return json_response({"data": serialize_paste(paste, include_content=False)}, 201)


@pastes_bp.get("/<string:slug>")
def get_paste(slug: str):
    user = _optional_user()
    paste = get_active_paste_by_slug(slug)
    if paste is None:
        raise APIError("not_found", "Paste not found", 404)
    if not can_view_paste(paste, user):
        raise APIError("not_found", "Paste not found", 404)

    provided_password = request.headers.get("X-Paste-Password")
    from app.services.paste_service import assert_paste_password

    assert_paste_password(paste, provided_password)

    increment_view_or_burn(paste)
    payload = serialize_paste(paste)
    db.session.commit()
    return json_response({"data": payload})


@pastes_bp.get("/<string:slug>/raw")
def get_paste_raw(slug: str):
    user = _optional_user()
    paste = get_active_paste_by_slug(slug)
    if paste is None:
        raise APIError("not_found", "Paste not found", 404)
    if not can_view_paste(paste, user):
        raise APIError("not_found", "Paste not found", 404)

    provided_password = request.headers.get("X-Paste-Password")
    from app.services.paste_service import assert_paste_password

    assert_paste_password(paste, provided_password)

    if paste.is_file:
        raise APIError("invalid_paste_type", "Use /download endpoint for file pastes", 400)

    increment_view_or_burn(paste)
    content = paste.content
    db.session.commit()
    return Response(content, mimetype="text/plain")


@pastes_bp.get("/<string:slug>/download")
def download_paste_file(slug: str):
    user = _optional_user()
    paste = get_active_paste_by_slug(slug)
    if paste is None:
        raise APIError("not_found", "Paste not found", 404)
    if not can_view_paste(paste, user):
        raise APIError("not_found", "Paste not found", 404)
    if not paste.is_file or not paste.file_path:
        raise APIError("invalid_paste_type", "Paste does not contain a file", 400)

    provided_password = request.headers.get("X-Paste-Password")
    from app.services.paste_service import assert_paste_password

    assert_paste_password(paste, provided_password)

    path = Path(paste.file_path)
    if not path.exists():
        raise APIError("file_not_found", "Stored file is missing", 404)

    increment_view_or_burn(paste)
    db.session.commit()
    return send_file(
        path,
        mimetype=paste.file_mime_type or "application/octet-stream",
        as_attachment=True,
        download_name=paste.file_name or path.name,
    )


@pastes_bp.patch("/<string:slug>")
@pastes_bp.put("/<string:slug>")
@jwt_required()
def update_paste(slug: str):
    user = require_active_user(get_jwt_identity())
    paste = get_active_paste_by_slug(slug)
    if paste is None:
        raise APIError("not_found", "Paste not found", 404)
    if not can_modify_paste(paste, user):
        raise APIError("forbidden", "You do not have permission to modify this paste", 403)

    payload = UpdatePasteSchema.model_validate(request.get_json(silent=False) or {})
    updates = payload.model_dump(exclude_unset=True)

    if "content" in updates and updates["content"] is not None:
        ensure_content_size(updates["content"], current_app.config["MAX_PASTE_BYTES"])
        paste.content = updates["content"]
    if "title" in updates:
        paste.title = updates["title"]
    if "language" in updates:
        paste.language = updates["language"]
    if "visibility" in updates and updates["visibility"] is not None:
        paste.visibility = PasteVisibility(updates["visibility"])
    if "burn_after_read" in updates and updates["burn_after_read"] is not None:
        paste.burn_after_read = bool(updates["burn_after_read"])
    if "collection_id" in updates:
        check_collection_owner(updates["collection_id"], paste.owner_id)
        paste.collection_id = updates["collection_id"]
    if "expires_in" in updates:
        set_paste_expiration(paste, updates["expires_in"])

    if updates.get("clear_password"):
        paste.password_hash = None
    elif "password" in updates:
        set_paste_password(paste, updates["password"])

    if "tags" in updates and updates["tags"] is not None:
        apply_tags(paste, updates["tags"])

    db.session.commit()
    return json_response({"data": serialize_paste(paste)})


@pastes_bp.delete("/<string:slug>")
@jwt_required()
def delete_paste(slug: str):
    user = require_active_user(get_jwt_identity())
    paste = get_active_paste_by_slug(slug)
    if paste is None:
        raise APIError("not_found", "Paste not found", 404)
    if not can_modify_paste(paste, user):
        raise APIError("forbidden", "You do not have permission to delete this paste", 403)

    paste.deleted_at = now_utc()
    delete_file_if_exists(paste.file_path)
    db.session.commit()
    return json_response({"data": {"message": "Paste deleted"}})


@pastes_bp.post("/<string:slug>/report")
@limiter.limit("20 per day")
def report_paste(slug: str):
    user = _optional_user()
    payload = ReportSchema.model_validate(request.get_json(silent=False) or {})

    paste = get_any_paste_by_slug(slug)
    if paste is None or (paste.expires_at is not None and paste.expires_at <= now_utc()):
        raise APIError("not_found", "Paste not found", 404)

    report = Report(
        paste_id=paste.id,
        reporter_user_id=user.id if user else None,
        reporter_ip=(request.headers.get("X-Forwarded-For") or request.remote_addr),
        reason=payload.reason,
        status=ReportStatus.OPEN,
    )
    db.session.add(report)
    db.session.commit()

    return (
        json_response(
            {
                "data": {
                    "id": str(report.id),
                    "status": report.status.value,
                    "created_at": report.created_at.isoformat(),
                }
            },
            201,
        )
    )
