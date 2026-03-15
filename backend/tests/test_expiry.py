from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select

from app.extensions import db
from app.models import Paste
from app.utils.time import now_utc


def test_expired_paste_returns_404(client):
    create_resp = client.post(
        "/api/v1/pastes",
        json={"content": "soon expired", "visibility": "public", "expires_in": "10m"},
    )
    assert create_resp.status_code == 201
    slug = create_resp.get_json()["data"]["slug"]

    paste = db.session.scalar(select(Paste).where(Paste.slug == slug))
    paste.expires_at = now_utc() - timedelta(minutes=1)
    db.session.commit()

    get_resp = client.get(f"/api/v1/pastes/{slug}")
    assert get_resp.status_code == 404


def test_clean_expired_command(app, client):
    create_resp = client.post(
        "/api/v1/pastes",
        json={"content": "cleanup", "visibility": "public", "expires_in": "10m"},
    )
    assert create_resp.status_code == 201
    slug = create_resp.get_json()["data"]["slug"]

    paste = db.session.scalar(select(Paste).where(Paste.slug == slug))
    paste.expires_at = now_utc() - timedelta(minutes=2)
    db.session.commit()

    runner = app.test_cli_runner()
    result = runner.invoke(args=["clean-expired"])
    assert result.exit_code == 0

    remaining = db.session.scalar(select(Paste).where(Paste.slug == slug))
    assert remaining is None
