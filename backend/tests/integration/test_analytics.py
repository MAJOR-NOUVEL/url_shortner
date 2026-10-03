def test_analytics_and_health_check(client, auth_user):
    # 1. Create link under auth_user
    create_resp = client.post("/api/urls", json={
        "url": "https://postgresql.org"
    }, headers=auth_user["headers"])
    url_id = create_resp.get_json()["id"]
    code = create_resp.get_json()["short_code"]

    # 2. Trigger redirects with different User-Agents and Referrers
    client.get(
        f"/{code}",
        headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) Mobile", "Referer": "https://t.co/abc"},
        follow_redirects=False
    )
    client.get(
        f"/{code}",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0", "Referer": "https://linkedin.com"},
        follow_redirects=False
    )

    # 3. Query analytics endpoint
    analytics_resp = client.get(f"/api/urls/{url_id}/analytics", headers=auth_user["headers"])
    assert analytics_resp.status_code == 200
    data = analytics_resp.get_json()

    assert data["total_clicks"] == 2
    assert data["unique_visitors"] >= 1
    assert len(data["clicks_per_day"]) == 30
    assert any(ref["name"] == "Twitter / X" for ref in data["top_referrers"])
    assert any(dev["name"] == "Mobile" for dev in data["devices"])

    # 4. Test /health endpoint
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.get_json()
    assert health_data["status"] == "healthy"
    assert health_data["database"] == "connected"
