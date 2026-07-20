"""Tests for the LLM schema enhancer."""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import pandas as pd

from n2s.ingest.schema import SchemaInferrer, TableSchema, ColumnSchema
from n2s.ingest.llm_enhancer import LlmSchemaEnhancer


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "订单号": [1, 2],
            "商品名称": ["item_a", "item_b"],
            "金额": [10.0, 20.0],
        }
    )


@pytest.fixture
def base_schema(sample_df):
    inferrer = SchemaInferrer()
    return inferrer.infer(sample_df, "orders")


def test_enhance_with_valid_llm_response(base_schema, sample_df):
    """When LLM returns valid JSON, schema is enhanced."""
    llm_response = json.dumps(
        {
            "table_name": "orders",
            "columns": [
                {"name": "order_id", "comment": "订单编号"},
                {"name": "product_name", "comment": "商品名称"},
                {"name": "amount", "comment": "金额"},
            ],
        }
    )

    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(return_value=MagicMock(content=llm_response))

    enhancer = LlmSchemaEnhancer(mock_llm)
    enhanced = enhancer.enhance(base_schema, sample_df)

    assert enhanced.table_name == "orders"
    names = [c.name for c in enhanced.columns]
    assert "order_id" in names
    assert "product_name" in names


def test_enhance_degrades_on_invalid_json(base_schema, sample_df):
    """When LLM returns garbage, fall back to base schema."""
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(return_value=MagicMock(content="not json at all"))

    enhancer = LlmSchemaEnhancer(mock_llm)
    enhanced = enhancer.enhance(base_schema, sample_df)

    # Should return original schema unchanged
    assert enhanced.table_name == base_schema.table_name
    assert [c.name for c in enhanced.columns] == [c.name for c in base_schema.columns]


def test_enhance_degrades_on_missing_fields(base_schema, sample_df):
    """When LLM JSON is missing expected fields, fall back."""
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(return_value=MagicMock(content='{"foo": "bar"}'))

    enhancer = LlmSchemaEnhancer(mock_llm)
    enhanced = enhancer.enhance(base_schema, sample_df)

    assert enhanced.table_name == base_schema.table_name


def test_enhance_with_no_llm(base_schema, sample_df):
    """When llm_service is None, return base schema unchanged."""
    enhancer = LlmSchemaEnhancer(llm_service=None)
    enhanced = enhancer.enhance(base_schema, sample_df)

    assert enhanced is base_schema
