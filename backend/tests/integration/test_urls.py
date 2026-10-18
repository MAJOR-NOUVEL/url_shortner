def test_create_url_anonymous(client):
    resp = client.post("/api/urls", json={
        "url": "https://python.org"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "short_code" in data
    assert data["original_url"] == "https://python.org"
    assert data["user_id"] is None

def test_create_url_with_custom_alias_and_collision(client, auth_user):
    # 1. Create with custom alias
    resp1 = client.post("/api/urls", json={
        "url": "https://flask.palletsprojects.com",
        "custom_alias": "flask-docs"
    }, headers=auth_user["headers"])
    assert resp1.status_code == 201
    assert resp1.get_json()["short_code"] == "flask-docs"

    # 2. Collision with same alias returns 409
    resp2 = client.post("/api/urls", json={
        "url": "https://palletsprojects.com",
        "custom_alias": "flask-docs"
    }, headers=auth_user["headers"])
    assert resp2.status_code == 409

def test_create_url_reserved_slug_rejected(client):
    resp = client.post("/api/urls", json={
        "url": "https://google.com",
        "custom_alias": "api"
    })
    assert resp.status_code == 400

def test_list_and_delete_user_urls(client, auth_user):
    # Create two links for auth_user
    client.post("/api/urls", json={"url": "https://link1.org"}, headers=auth_user["headers"])
    r2 = client.post("/api/urls", json={"url": "https://link2.org"}, headers=auth_user["headers"])
    link2_id = r2.get_json()["id"]

    # List links
    list_resp = client.post if False else client.get("/api/urls", headers=auth_user["headers"])
    assert list_resp.status_code == 200
    links = list_resp.get_json()
    assert len(links) == 2

    # Delete link2
    del_resp = client.delete(f"/api/urls/{link2_id}", headers=auth_user["headers"])
    assert del_resp.status_code == 200

    # Verify link2 is removed from list
    list_after = client.get("/api/urls", headers=auth_user["headers"])
    assert len(list_after.get_json()) == 1

def test_resolve_short_url_lifecycle(client):
    # 1. Create a link
    resp = client.post("/api/urls", json={"url": "https://developer.mozilla.org"})
    assert resp.status_code == 201
    code = resp.get_json()["short_code"]

    # 2. Resolve link via API
    resolve_resp = client.get(f"/api/urls/resolve/{code}")
    assert resolve_resp.status_code == 200
    res_data = resolve_resp.get_json()
    assert res_data["short_code"] == code
    assert res_data["original_url"] == "https://developer.mozilla.org"

    # 3. Resolve unknown link returns 404
    unknown_resp = client.get("/api/urls/resolve/nonexistent-code-12345")
    assert unknown_resp.status_code == 404

def test_create_url_respects_frontend_origin_header(client):
    # When request comes from Vercel frontend or custom domain:
    resp = client.post(
        "/api/urls",
        json={"url": "https://vitejs.dev"},
        headers={"Origin": "https://bitroot.vercel.app"}
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["short_url"].startswith("https://bitroot.vercel.app/")

