"""End-to-end tests for the DataIngestor engine."""

from pathlib import Path
import pytest
import pandas as pd
import sqlite3

from n2s.ingest.engine import DataIngestor


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parent.parent / "fixtures" / "ingest"


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_engine.db")


@pytest.fixture
def ingestor(db_path):
    return DataIngestor(db_url=f"sqlite:///{db_path}", llm_service=None)


def test_ingest_directory_end_to_end(ingestor, fixtures_dir):
    """Ingest the test fixtures directory and verify tables exist."""
    result = ingestor.ingest_directory_sync(str(fixtures_dir))

    assert result.success
    assert result.total_files >= 2
    assert result.succeeded >= 2
    assert result.failed == 0
    assert "sample" in result.tables_created

    # Verify data is queryable
    tables = ingestor.list_tables()
    assert "sample" in tables


def test_ingest_directory_nonexistent(ingestor):
    with pytest.raises(FileNotFoundError):
        ingestor.ingest_directory_sync("/nonexistent/path")


def test_ingest_single_file(ingestor, fixtures_dir):
    result = ingestor.ingest_file_sync(str(fixtures_dir / "sample.csv"), table_name="my_table")

    assert result.success
    assert "my_table" in result.tables_created
    assert ingestor.list_tables() == ["my_table"] or "my_table" in ingestor.list_tables()


def test_progress_tracking(ingestor, fixtures_dir):
    ingestor.ingest_directory_sync(str(fixtures_dir))

    progress = ingestor.get_progress()
    assert progress.status == "done"
    assert progress.total_files >= 2
    assert progress.completed >= 2
