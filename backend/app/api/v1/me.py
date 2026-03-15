from __future__ import annotations

import uuid

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import desc, func, or_, select

from app.extensions import db
from app.models import Collection, Paste
from app.schemas.collection import CreateCollectionSchema
from app.schemas.common import parse_pagination
from app.services.auth_service import require_active_user
from app.services.paste_service import serialize_paste
from app.utils.errors import APIError
from app.utils.responses import json_response
from app.utils.time import now_utc

me_bp = Blueprint("me_v1", __name__, url_prefix="/me")


@me_bp.get("/pastes")
@jwt_required()
def my_pastes():
    user = require_active_user(get_jwt_identity())
    pagination = parse_pagination(request.args)
    page, limit = pagination.page, pagination.limit

    now = now_utc()
    base_query = select(Paste).where(
        Paste.owner_id == user.id,
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


@me_bp.get("/collections")
@jwt_required()
def list_collections():
    user = require_active_user(get_jwt_identity())
    collections = db.session.scalars(
        select(Collection).where(Collection.owner_id == user.id).order_by(Collection.name.asc())
    ).all()
    data = [
        {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        }
        for item in collections
    ]
    return json_response({"data": data})


@me_bp.post("/collections")
@jwt_required()
def create_collection():
    user = require_active_user(get_jwt_identity())
    payload = CreateCollectionSchema.model_validate(request.get_json(silent=False) or {})

    exists = db.session.scalar(
        select(Collection).where(Collection.owner_id == user.id, Collection.name == payload.name)
    )
    if exists:
        raise APIError("collection_exists", "Collection with this name already exists", 409)

    collection = Collection(owner_id=user.id, name=payload.name, description=payload.description)
    db.session.add(collection)
    db.session.commit()

    return (
        json_response(
            {
                "data": {
                    "id": str(collection.id),
                    "name": collection.name,
                    "description": collection.description,
                    "created_at": collection.created_at.isoformat(),
                }
            },
            201,
        )
    )


@me_bp.delete("/collections/<uuid:collection_id>")
@jwt_required()
def delete_collection(collection_id: uuid.UUID):
    user = require_active_user(get_jwt_identity())
    collection = db.session.get(Collection, collection_id)
    if collection is None or collection.owner_id != user.id:
        raise APIError("collection_not_found", "Collection not found", 404)

    db.session.delete(collection)
    db.session.commit()
    return json_response({"data": {"message": "Collection deleted"}})
