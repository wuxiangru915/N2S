"""Integration test: after ingestion, Agent tools can see and query new data."""

import asyncio
import sqlite3
from pathlib import Path
import pytest

from n2s.ingest.engine import DataIngestor
from n2s.demo.tools.schema import ExplainSchemaTool, ExplainSchemaToolArgs
from n2s.core.tool import ToolContext
from n2s.core.user import User
from n2s.integrations.local.agent_memory import DemoAgentMemory


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parent.parent / "fixtures" / "ingest"


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "agent_integration.db")


@pytest.fixture
def context():
    return ToolContext(
        user=User(id="test", username="test", email="test@example.com"),
        conversation_id="test",
        request_id="test",
        agent_memory=DemoAgentMemory(),
        metadata={},
    )


def test_explain_schema_after_ingest(fixtures_dir, db_path, context):
    """After ingestion, ExplainSchemaTool sees the new tables."""
    # Ingest
    ingestor = DataIngestor(db_url=f"sqlite:///{db_path}", llm_service=None)
    ingestor.ingest_directory_sync(str(fixtures_dir))

    # Use schema tool
    tool = ExplainSchemaTool(database_path=db_path)
    result = asyncio.run(tool.execute(context, ExplainSchemaToolArgs()))

    assert result.success
    assert "sample" in result.result_for_llm.lower()


def test_query_data_after_ingest(fixtures_dir, db_path):
    """After ingestion, the data is queryable via SQL."""
    ingestor = DataIngestor(db_url=f"sqlite:///{db_path}", llm_service=None)
    ingestor.ingest_directory_sync(str(fixtures_dir))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sample")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 2  # sample.json (2 rows) processed last, overwrites sample.csv (3 rows)


def test_table_info_after_ingest(fixtures_dir, db_path):
    """get_table_info returns correct metadata after ingestion."""
    ingestor = DataIngestor(db_url=f"sqlite:///{db_path}", llm_service=None)
    ingestor.ingest_directory_sync(str(fixtures_dir))

    tables = ingestor.list_tables()
    assert "sample" in tables

    info = ingestor.get_table_info("sample")
    assert info["name"] == "sample"
    assert info["rows"] == 2  # sample.json overwrites sample.csv (replace mode)
    assert info["columns"] >= 2
