"""
Unit tests — test app logic directly via Flask's test client.
No running server or Docker container required.
"""

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data


def test_version_returns_expected_keys(client):
    response = client.get("/version")
    assert response.status_code == 200
    data = response.get_json()
    assert "app" in data
    assert "git_sha" in data
    assert "environment" in data


def test_excuse_dev_environment(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "dev")
    response = client.get("/excuse")
    assert response.status_code == 200
    data = response.get_json()
    assert data["environment"] == "dev"
    assert "jira_ticket" in data  # dev-only field


def test_excuse_prod_environment(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")
    response = client.get("/excuse")
    assert response.status_code == 200
    data = response.get_json()
    assert data["environment"] == "prod"
    assert "incident_id" in data  # prod-only field
    assert "jira_ticket" not in data


def test_oncall_prod_is_always_engaged(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")
    response = client.get("/oncall")
    data = response.get_json()
    assert data["oncall_status"] == "Engaged"
    assert data["acknowledged"] is True


def test_index_lists_endpoints(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "endpoints" in data
