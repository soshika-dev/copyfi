from __future__ import annotations

import uuid

from flask import Blueprint, request
from sqlalchemy import desc, func, select

from app.extensions import db
from app.models import Paste, Report, ReportStatus, User
from app.schemas.admin import BanUserSchema, UpdateReportStatusSchema
from app.schemas.common import parse_pagination
from app.utils.file_storage import delete_file_if_exists
from app.utils.decorators import admin_required
from app.utils.errors import APIError
from app.utils.responses import json_response
from app.utils.time import now_utc

admin_bp = Blueprint("admin_v1", __name__, url_prefix="/admin")


@admin_bp.get("/reports")
@admin_required
def list_reports():
    pagination = parse_pagination(request.args)
    page, limit = pagination.page, pagination.limit

    status_filter = request.args.get("status")
    base_query = select(Report)
    if status_filter:
        try:
            status = ReportStatus(status_filter)
        except ValueError as exc:
            raise APIError("invalid_status", "Invalid report status", 422) from exc
        base_query = base_query.where(Report.status == status)

    total = db.session.scalar(select(func.count()).select_from(base_query.subquery()))
    reports = db.session.scalars(
        base_query.order_by(desc(Report.created_at)).offset((page - 1) * limit).limit(limit)
    ).all()

    data = [
        {
            "id": str(report.id),
            "paste_id": str(report.paste_id),
            "reporter_user_id": str(report.reporter_user_id) if report.reporter_user_id else None,
            "reporter_ip": report.reporter_ip,
            "reason": report.reason,
            "status": report.status.value,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
        for report in reports
    ]

    return json_response(
        {
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": int(total or 0),
                "pages": (int(total or 0) + limit - 1) // limit,
            },
        }
    )


@admin_bp.patch("/reports/<uuid:report_id>")
@admin_required
def update_report(report_id: uuid.UUID):
    payload = UpdateReportStatusSchema.model_validate(request.get_json(silent=False) or {})
    report = db.session.get(Report, report_id)
    if report is None:
        raise APIError("report_not_found", "Report not found", 404)

    report.status = ReportStatus(payload.status)
    db.session.commit()
    return json_response(
        {
            "data": {
                "id": str(report.id),
                "status": report.status.value,
                "updated_at": report.updated_at.isoformat(),
            }
        }
    )


@admin_bp.delete("/pastes/<string:slug>")
@admin_required
def admin_delete_paste(slug: str):
    paste = db.session.scalar(select(Paste).where(Paste.slug == slug, Paste.deleted_at.is_(None)))
    if paste is None:
        raise APIError("not_found", "Paste not found", 404)

    paste.deleted_at = now_utc()
    delete_file_if_exists(paste.file_path)
    db.session.commit()
    return json_response({"data": {"message": "Paste deleted"}})


@admin_bp.patch("/users/<uuid:user_id>/ban")
@admin_required
def admin_ban_user(user_id: uuid.UUID):
    payload = BanUserSchema.model_validate(request.get_json(silent=False) or {})
    user = db.session.get(User, user_id)
    if user is None:
        raise APIError("user_not_found", "User not found", 404)

    user.is_banned = payload.is_banned
    db.session.commit()
    return json_response(
        {
            "data": {
                "id": str(user.id),
                "username": user.username,
                "is_banned": user.is_banned,
            }
        }
    )
