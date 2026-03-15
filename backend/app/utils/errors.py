from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from flask import Flask, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


@dataclass
class APIError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def handle_api_error(err: APIError):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        return (
            jsonify(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Input validation failed",
                        "details": {"issues": err.errors()},
                    }
                }
            ),
            422,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(err: HTTPException):
        return (
            jsonify(
                {
                    "error": {
                        "code": "http_error",
                        "message": err.description,
                        "details": {"status": err.code},
                    }
                }
            ),
            err.code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        app.logger.exception("Unhandled error", exc_info=err)
        return (
            jsonify(
                {
                    "error": {
                        "code": "internal_server_error",
                        "message": "An unexpected error occurred",
                        "details": {},
                    }
                }
            ),
            500,
        )
