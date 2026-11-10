import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_and_root():
    """Verify server status and documentation routes."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "healthy"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json() == {"status": "ok"}

def test_auth_unauthorized_access():
    """Verify protected endpoints reject requests without a valid token."""
    res = client.get("/api/v1/urls")
    assert res.status_code == 401
    assert "detail" in res.json()

def test_auth_invalid_credentials():
    """Verify login fails with wrong credentials."""
    res = client.post("/api/v1/auth/login", json={"username": "wrong_user", "password": "wrong_password"})
    assert res.status_code == 401

def test_full_url_crud_lifecycle():
    """
    Test complete lifecycle:
    1. Login with demo admin account
    2. Inspect authenticated user profile (/me)
    3. Verify initial URLs list is empty (no dummy data)
    4. Create a new URL entry
    5. Retrieve the URL entry by ID
    6. Search & filter the URL entry
    7. Update fields (title, category, environment)
    8. Toggle status (active <-> inactive)
    9. Delete the URL entry
    10. Verify 404 on deleted item
    11. Logout
    """
    # 1. Login
    login_resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert body["success"] is True
    assert "token" in body
    token = body["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get current user
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "Administrator"

    # 3. List URLs (should start clean with no dummy entries)
    list_resp = client.get("/api/v1/urls", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json() == []

    # 4. Add a real stream URL
    payload = {
        "title": "Corporate HQ Main Feed",
        "url": "https://stream.internal.corp/live/lobby.m3u8",
        "category": "Corporate",
        "description": "Lobby screens high-res broadcast",
        "environment": "production",
        "status": "active",
        "refreshInterval": 30
    }
    create_resp = client.post("/api/v1/urls", json=payload, headers=headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["title"] == payload["title"]
    assert created["name"] == payload["title"]  # Flutter compatibility
    assert created["url"] == payload["url"]
    assert created["address"] == payload["url"]  # Flutter compatibility
    assert created["status"] == "active"
    url_id = created["id"]

    # 5. Get by ID
    get_resp = client.get(f"/api/v1/urls/{url_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == url_id

    # 6. Search & Filters
    search_resp = client.get("/api/v1/urls?search=Corporate", headers=headers)
    assert search_resp.status_code == 200
    assert len(search_resp.json()) == 1

    empty_search = client.get("/api/v1/urls?search=NonExistent", headers=headers)
    assert empty_search.status_code == 200
    assert len(empty_search.json()) == 0

    category_filter = client.get("/api/v1/urls?category=Corporate", headers=headers)
    assert category_filter.status_code == 200
    assert len(category_filter.json()) == 1

    # 7. Update URL
    update_payload = {
        "title": "Corporate HQ Main Feed (4K HDR)",
        "refreshInterval": 60,
        "environment": "staging"
    }
    update_resp = client.put(f"/api/v1/urls/{url_id}", json=update_payload, headers=headers)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["title"] == "Corporate HQ Main Feed (4K HDR)"
    assert updated["name"] == "Corporate HQ Main Feed (4K HDR)"
    assert updated["refreshInterval"] == 60
    assert updated["environment"] == "staging"

    # 8. Toggle status
    toggle_resp = client.patch(f"/api/v1/urls/{url_id}/toggle-status", headers=headers)
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["status"] == "inactive"

    toggle_back = client.patch(f"/api/v1/urls/{url_id}/toggle-status", headers=headers)
    assert toggle_back.status_code == 200
    assert toggle_back.json()["status"] == "active"

    # 9. Delete URL
    del_resp = client.delete(f"/api/v1/urls/{url_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 10. Verify 404 on deleted item
    not_found = client.get(f"/api/v1/urls/{url_id}", headers=headers)
    assert not_found.status_code == 404

    # 11. Logout
    logout_resp = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["success"] is True
