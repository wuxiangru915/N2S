"""Tests for the database loader."""

import sqlite3
from pathlib import Path
import pytest
import pandas as pd

from n2s.ingest.schema import SchemaInferrer, ColumnSchema, TableSchema
from n2s.ingest.loader import DatabaseLoader


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def loader(db_path):
    return DatabaseLoader(f"sqlite:///{db_path}")


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["alice", "bob", "charlie"],
            "value": [10.5, 20.0, 30.5],
        }
    )


@pytest.fixture
def inferrer():
    return SchemaInferrer()


def test_load_creates_table(loader, sample_df, inferrer):
    schema = inferrer.infer(sample_df, "products")
    loader.load(sample_df, schema, mode="replace")

    tables = loader.list_tables()
    assert "products" in tables


def test_load_row_count(loader, sample_df, inferrer):
    schema = inferrer.infer(sample_df, "products")
    loader.load(sample_df, schema, mode="replace")

    import sqlalchemy

    engine = sqlalchemy.create_engine(loader.db_url)
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT COUNT(*) FROM products")
        count = result.fetchone()[0]
    assert count == 3


def test_load_replace_mode(loader, sample_df, inferrer):
    schema = inferrer.infer(sample_df, "products")
    loader.load(sample_df, schema, mode="replace")
    loader.load(sample_df, schema, mode="replace")  # second time should replace

    engine = __import__("sqlalchemy").create_engine(loader.db_url)
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT COUNT(*) FROM products")
        count = result.fetchone()[0]
    assert count == 3  # not 6


def test_load_append_mode(loader, sample_df, inferrer):
    schema = inferrer.infer(sample_df, "products")
    loader.load(sample_df, schema, mode="replace")
    loader.load(sample_df, schema, mode="append")

    engine = __import__("sqlalchemy").create_engine(loader.db_url)
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT COUNT(*) FROM products")
        count = result.fetchone()[0]
    assert count == 6


def test_list_tables_after_load(loader, sample_df, inferrer):
    schema = inferrer.infer(sample_df, "test_table")
    loader.load(sample_df, schema, mode="replace")

    tables = loader.list_tables()
    assert "test_table" in tables
