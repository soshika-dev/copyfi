from __future__ import annotations

import logging
import os

from flask import Flask, jsonify

from app.api.v1 import api_v1_bp
from app.commands import register_commands
from app.config import CONFIG_BY_NAME, DevelopmentConfig
from app.extensions import init_extensions, jwt
from app.services.auth_service import is_refresh_token_revoked
from app.utils.errors import register_error_handlers


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    env = config_name or os.getenv("FLASK_ENV", "development")
    config_class = CONFIG_BY_NAME.get(env, DevelopmentConfig)
    app.config.from_object(config_class)

    _configure_logging(app)
    init_extensions(app)
    _register_jwt_callbacks(app)
    register_error_handlers(app)

    with app.app_context():
        from app import models  # noqa: F401

    app.register_blueprint(api_v1_bp)
    register_commands(app)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


def _configure_logging(app: Flask) -> None:
    level_name = app.config.get("LOG_LEVEL", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _register_jwt_callbacks(app: Flask) -> None:
    @jwt.token_in_blocklist_loader
    def token_in_blocklist(_jwt_header, jwt_payload):
        token_type = jwt_payload.get("type")
        if token_type != "refresh":
            return False
        return is_refresh_token_revoked(jwt_payload["jti"])

    @jwt.unauthorized_loader
    def unauthorized_loader(message: str):
        return (
            jsonify(
                {
                    "error": {
                        "code": "missing_token",
                        "message": message,
                        "details": {},
                    }
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_loader(message: str):
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_token",
                        "message": message,
                        "details": {},
                    }
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_loader(_jwt_header, _jwt_payload):
        return (
            jsonify(
                {
                    "error": {
                        "code": "token_expired",
                        "message": "Token has expired",
                        "details": {},
                    }
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_loader(_jwt_header, _jwt_payload):
        return (
            jsonify(
                {
                    "error": {
                        "code": "token_revoked",
                        "message": "Token has been revoked",
                        "details": {},
                    }
                }
            ),
            401,
        )
