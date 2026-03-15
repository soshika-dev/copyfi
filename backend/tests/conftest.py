from __future__ import annotations

import os
import tempfile

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    fd, path = tempfile.mkstemp(prefix="pastehub-test-", suffix=".db")
    os.close(fd)
    os.environ["TEST_DATABASE_URL"] = f"sqlite+pysqlite:///{path}"

    flask_app = create_app("testing")
    flask_app.config.update(
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-jwt-secret",
        RATELIMIT_ENABLED=False,
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    if os.path.exists(path):
        os.unlink(path)
    os.environ.pop("TEST_DATABASE_URL", None)
