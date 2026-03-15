from __future__ import annotations


def test_register_login_refresh_logout(client):
    register_resp = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "Secret123", "email": "alice@example.com"},
    )
    assert register_resp.status_code == 201
    register_data = register_resp.get_json()["data"]
    assert register_data["user"]["username"] == "alice"
    assert register_data["access_token"]
    assert register_data["refresh_token"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "Secret123"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.get_json()["data"]

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {login_data['refresh_token']}"},
    )
    assert refresh_resp.status_code == 200
    refreshed = refresh_resp.get_json()["data"]
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]

    logout_resp = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {refreshed['refresh_token']}"},
    )
    assert logout_resp.status_code == 200

    revoked_refresh_resp = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refreshed['refresh_token']}"},
    )
    assert revoked_refresh_resp.status_code == 401
    assert revoked_refresh_resp.get_json()["error"]["code"] == "token_revoked"
