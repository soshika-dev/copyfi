from __future__ import annotations

from flask import jsonify


def json_response(payload: dict, status: int = 200):
    return jsonify(payload), status
