from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.extensions import limiter
from app.schemas.auth import LoginSchema, RegisterSchema
from app.services.auth_service import (
    authenticate_user,
    create_user,
    issue_tokens,
    require_active_user,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.utils.responses import json_response

auth_bp = Blueprint("auth_v1", __name__, url_prefix="/auth")


@auth_bp.post("/register")
@limiter.limit("10 per hour")
def register():
    payload = RegisterSchema.model_validate(request.get_json(silent=False) or {})
    user = create_user(payload.username, payload.password, payload.email)
    tokens = issue_tokens(user)
    return (
        json_response(
            {
                "data": {
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value,
                    },
                    **tokens,
                }
            },
            201,
        )
    )


@auth_bp.post("/login")
@limiter.limit("20 per hour")
def login():
    payload = LoginSchema.model_validate(request.get_json(silent=False) or {})
    user = authenticate_user(payload.username, payload.password)
    tokens = issue_tokens(user)
    return json_response(
        {
            "data": {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                },
                **tokens,
            }
        }
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
@limiter.limit("60 per day")
def refresh():
    user = require_active_user(get_jwt_identity())
    claims = get_jwt()
    tokens = rotate_refresh_token(user, claims["jti"])
    return json_response({"data": tokens})


@auth_bp.post("/logout")
@jwt_required(refresh=True)
def logout():
    claims = get_jwt()
    revoke_refresh_token(claims["jti"])
    return json_response({"data": {"message": "Logged out"}})
