"""
System tests — run against a live container (see CI workflow).
Requires the app to actually be running (see BASE_URL).
"""

import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5050")


def test_health_endpoint_live():
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metrics_endpoint_live():
    response = requests.get(f"{BASE_URL}/metrics", timeout=5)
    assert response.status_code == 200
    assert "requests_served" in response.json()


def test_multiple_requests_increment_counter():
    r1 = requests.get(f"{BASE_URL}/health", timeout=5).json()
    r2 = requests.get(f"{BASE_URL}/health", timeout=5).json()
    assert r2["requests_served"] > r1["requests_served"]


def test_container_responds_within_timeout():
    response = requests.get(f"{BASE_URL}/", timeout=2)
    assert response.status_code == 200
