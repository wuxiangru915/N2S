"""Test that ExplainSchemaTool works with SQLAlchemy inspect()."""

import asyncio
import sqlite3
import pytest

from n2s.core.tool import ToolContext, ToolResult
from n2s.core.user import User
from n2s.integrations.local.agent_memory import DemoAgentMemory
from n2s.demo.tools.schema import ExplainSchemaTool


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "schema_test.db")
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
    )
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, product_id INTEGER, qty INTEGER)"
    )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def context():
    return ToolContext(
        user=User(id="test", username="test", email="test@example.com"),
        conversation_id="test",
        request_id="test",
        agent_memory=DemoAgentMemory(),
        metadata={},
    )


def test_list_all_tables(db_path, context):
    tool = ExplainSchemaTool(database_path=db_path)
    result = asyncio.run(tool.execute(context, tool.get_args_schema()()))

    assert result.success
    assert "products" in result.result_for_llm
    assert "orders" in result.result_for_llm


def test_list_specific_table(db_path, context):
    from n2s.demo.tools.schema import ExplainSchemaToolArgs

    tool = ExplainSchemaTool(database_path=db_path)
    args = ExplainSchemaToolArgs(tables=["products"])
    result = asyncio.run(tool.execute(context, args))

    assert result.success
    assert "products" in result.result_for_llm
    assert "orders" not in result.result_for_llm


def test_shows_column_types(db_path, context):
    tool = ExplainSchemaTool(database_path=db_path)
    result = asyncio.run(tool.execute(context, tool.get_args_schema()()))

    assert "id" in result.result_for_llm
    assert "INTEGER" in result.result_for_llm
    assert "name" in result.result_for_llm
    assert "TEXT" in result.result_for_llm
    assert "price" in result.result_for_llm
    assert "REAL" in result.result_for_llm
