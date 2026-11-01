def make_service(client, name):
    response = client.post("/services", json={"name": name, "description": "test"})
    assert response.status_code == 201
    return response.json()


def test_create_service(client):
    data = make_service(client, "test-create")
    assert data["name"] == "test-create"
    assert "id" in data and "created_at" in data


def test_duplicate_service_returns_409(client):
    make_service(client, "test-dup")
    response = client.post("/services", json={"name": "test-dup"})
    assert response.status_code == 409


def test_alert_for_missing_service_returns_404(client):
    response = client.post("/alerts", json={"service_id": 999999, "title": "x"})
    assert response.status_code == 404


def test_invalid_severity_returns_422(client):
    service = make_service(client, "test-sev")
    response = client.post(
        "/alerts",
        json={"service_id": service["id"], "title": "x", "severity": "urgent"},
    )
    assert response.status_code == 422


def test_unknown_field_returns_422(client):
    service = make_service(client, "test-extra")
    response = client.post(
        "/alerts",
        json={"service_id": service["id"], "title": "x", "serverity": "info"},
    )
    assert response.status_code == 422


def test_resolve_sets_and_clears_resolved_at(client):
    service = make_service(client, "test-resolve")
    alert = client.post(
        "/alerts", json={"service_id": service["id"], "title": "x"}
    ).json()
    path = f"/alerts/{alert['id']}/status"

    resolved = client.patch(path, json={"status": "resolved"})
    assert resolved.status_code == 200
    assert resolved.json()["resolved_at"] is not None

    reopened = client.patch(path, json={"status": "open"})
    assert reopened.json()["resolved_at"] is None


def test_list_filters_and_pagination(client):
    service = make_service(client, "test-list")
    for i in range(3):
        client.post(
            "/alerts",
            json={"service_id": service["id"], "title": f"a{i}", "severity": "critical"},
        )
    response = client.get(
        "/alerts",
        params={"service_id": service["id"], "severity": "critical", "limit": 2},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_limit_above_maximum_returns_422(client):
    response = client.get("/alerts", params={"limit": 500})
    assert response.status_code == 422


def test_delete_service_with_alerts_returns_409(client):
    service = make_service(client, "test-delete")
    client.post("/alerts", json={"service_id": service["id"], "title": "x"})
    response = client.delete(f"/services/{service['id']}")
    assert response.status_code == 409
    assert client.get(f"/services/{service['id']}").status_code == 200