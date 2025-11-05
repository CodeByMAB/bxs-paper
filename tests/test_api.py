#!/usr/bin/env python3
"""Tests for FastAPI endpoints."""
import os
import sys
import tempfile
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_db():
    """Create temporary test database."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)

    conn = sqlite3.connect(path)
    # Create schema
    schema_path = os.path.join(os.path.dirname(__file__), "..", "data", "schema.sql")
    if not os.path.exists(schema_path):
        # Try alternative path for CI
        schema_path = os.path.join("data", "schema.sql")
    with open(schema_path, "r") as f:
        conn.executescript(f.read())

    # Insert test data
    conn.execute(
        """INSERT INTO blocks (h, t, sigma, S, lambda, I)
           VALUES (800000, 1709251200, 6.25, 19500000, 1.0/600, 5.34e-10)"""
    )
    conn.execute(
        """INSERT INTO wallet (t, W, A, i, mu, CP, SSR, f)
           VALUES (1709251200, 12000000, 18000000, 4700, 3800, 2500000, 1.5, 100.0)"""
    )
    conn.execute(
        """INSERT INTO metrics (t, S_cum, BXS_cum)
           VALUES (1709251200, 1000000, 50000000)"""
    )
    conn.commit()
    conn.close()

    yield path

    os.unlink(path)


@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    # Import here after path is set
    from code.app import main as main_module  # noqa: E402

    # Patch the DB_PATH in the module and environment
    original_db_path = main_module.DB_PATH
    original_env_db = os.environ.get("DB_PATH")

    # Set environment variable first, then patch module
    os.environ["DB_PATH"] = test_db
    main_module.DB_PATH = test_db

    from code.app.main import app  # noqa: E402

    client = TestClient(app)
    yield client

    # Restore original
    main_module.DB_PATH = original_db_path
    if original_env_db:
        os.environ["DB_PATH"] = original_env_db
    else:
        os.environ.pop("DB_PATH", None)


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data


def test_metrics_latest(client):
    """Test /metrics/latest endpoint."""
    response = client.get("/metrics/latest")
    assert response.status_code == 200
    data = response.json()
    assert "f" in data
    assert "S" in data
    assert "BXS" in data
    assert isinstance(data["f"], (int, float))
    assert isinstance(data["S"], (int, float))
    assert isinstance(data["BXS"], (int, float))


def test_metrics_range(client):
    """Test /metrics/range endpoint."""
    start = 1709251100
    end = 1709251300
    response = client.get(f"/metrics/range?start={start}&end={end}")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data


def test_alerts_recent(client):
    """Test /alerts/recent endpoint."""
    response = client.get("/alerts/recent")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_admin_recompute_disabled(client):
    """Test /admin/recompute is disabled by default."""
    response = client.post("/admin/recompute")
    assert response.status_code == 403


def test_healthz(client):
    """Test /healthz endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}
