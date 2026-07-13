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


def test_requests_served_is_present_and_valid():
    """
    Note: requests_served is tracked per-worker-process (in-memory), so with
    multiple Gunicorn workers, consecutive requests may hit different workers
    and report different counts. This test validates the field's shape, not
    strict ordering across an unknown number of worker processes.
    """
    response = requests.get(f"{BASE_URL}/health", timeout=5).json()
    assert isinstance(response["requests_served"], int)
    assert response["requests_served"] >= 1


def test_container_responds_within_timeout():
    response = requests.get(f"{BASE_URL}/", timeout=2)
    assert response.status_code == 200
