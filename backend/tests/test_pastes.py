from __future__ import annotations


def register_and_login(client, username: str = "user1") -> str:
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "Secret123", "email": f"{username}@example.com"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "Secret123"},
    )
    return login.get_json()["data"]["access_token"]


def test_private_paste_visibility(client):
    access = register_and_login(client, "owner")

    create_resp = client.post(
        "/api/v1/pastes",
        json={
            "title": "private",
            "content": "top secret",
            "visibility": "private",
            "expires_in": "never",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert create_resp.status_code == 201
    slug = create_resp.get_json()["data"]["slug"]

    anonymous_read = client.get(f"/api/v1/pastes/{slug}")
    assert anonymous_read.status_code == 404

    owner_read = client.get(f"/api/v1/pastes/{slug}", headers={"Authorization": f"Bearer {access}"})
    assert owner_read.status_code == 200
    assert owner_read.get_json()["data"]["content"] == "top secret"


def test_password_protected_paste(client):
    create_resp = client.post(
        "/api/v1/pastes",
        json={
            "content": "hello",
            "visibility": "unlisted",
            "password": "pw123",
            "expires_in": "never",
        },
    )
    assert create_resp.status_code == 201
    slug = create_resp.get_json()["data"]["slug"]

    without_password = client.get(f"/api/v1/pastes/{slug}")
    assert without_password.status_code == 401

    with_password = client.get(f"/api/v1/pastes/{slug}", headers={"X-Paste-Password": "pw123"})
    assert with_password.status_code == 200
    assert with_password.get_json()["data"]["content"] == "hello"


def test_owner_update_and_delete(client):
    access = register_and_login(client, "editor")

    create_resp = client.post(
        "/api/v1/pastes",
        json={"content": "before", "visibility": "public"},
        headers={"Authorization": f"Bearer {access}"},
    )
    slug = create_resp.get_json()["data"]["slug"]

    update_resp = client.patch(
        f"/api/v1/pastes/{slug}",
        json={"content": "after", "tags": ["python", "flask"]},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert update_resp.status_code == 200
    body = update_resp.get_json()["data"]
    assert body["content"] == "after"
    assert body["tags"] == ["flask", "python"]

    delete_resp = client.delete(
        f"/api/v1/pastes/{slug}", headers={"Authorization": f"Bearer {access}"}
    )
    assert delete_resp.status_code == 200

    read_after_delete = client.get(f"/api/v1/pastes/{slug}")
    assert read_after_delete.status_code == 404
