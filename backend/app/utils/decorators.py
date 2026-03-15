from __future__ import annotations

from functools import wraps
from typing import Callable

from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import UserRole
from app.services.auth_service import require_active_user
from app.utils.errors import APIError


def admin_required(func: Callable):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = require_active_user(get_jwt_identity())
        if user.role != UserRole.ADMIN:
            raise APIError("forbidden", "Admin role required", 403)
        return func(*args, **kwargs)

    return wrapper
