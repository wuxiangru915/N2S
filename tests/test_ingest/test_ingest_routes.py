"""Integration tests for ingest API routes."""

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from n2s.ingest.routes import register_ingest_routes


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parent.parent / "fixtures" / "ingest"


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_routes.db")


@pytest.fixture
def client(db_path):
    """Create a minimal app with only ingest routes."""
    app = FastAPI()
    db_url = f"sqlite:///{db_path}"
    register_ingest_routes(app, default_db_url=db_url, llm_service=None)
    return TestClient(app)


def test_ingest_directory(client, fixtures_dir):
    """POST /api/ingest/directory should return task_id and ingest files."""
    response = client.post(
        "/api/ingest/directory",
        json={"dir_path": str(fixtures_dir)},
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["total_files"] >= 2


def test_ingest_progress(client, fixtures_dir):
    """GET /api/ingest/progress/{task_id} should return progress."""
    response = client.post(
        "/api/ingest/directory",
        json={"dir_path": str(fixtures_dir)},
    )
    task_id = response.json()["task_id"]

    progress_response = client.get(f"/api/ingest/progress/{task_id}")
    assert progress_response.status_code == 200
    progress = progress_response.json()
    assert progress["status"] in ("running", "done", "pending")
    assert progress["total_files"] >= 2


def test_ingest_tables(client, fixtures_dir):
    """GET /api/ingest/tables should list tables after ingestion."""
    client.post(
        "/api/ingest/directory",
        json={"dir_path": str(fixtures_dir)},
    )

    response = client.get("/api/ingest/tables")
    assert response.status_code == 200
    tables = response.json()
    table_names = [t["name"] for t in tables]
    assert "sample" in table_names


def test_ingest_file(client, fixtures_dir):
    """POST /api/ingest/file should ingest a single file."""
    response = client.post(
        "/api/ingest/file",
        json={
            "file_path": str(fixtures_dir / "sample.csv"),
            "table_name": "custom_table",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "custom_table" in data["tables_created"]
