from __future__ import annotations

from flask import Blueprint

from app.api.v1.admin import admin_bp
from app.api.v1.auth import auth_bp
from app.api.v1.me import me_bp
from app.api.v1.pastes import pastes_bp

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

api_v1_bp.register_blueprint(auth_bp)
api_v1_bp.register_blueprint(pastes_bp)
api_v1_bp.register_blueprint(me_bp)
api_v1_bp.register_blueprint(admin_bp)
