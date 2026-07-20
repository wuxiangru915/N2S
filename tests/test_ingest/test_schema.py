"""Tests for the schema inferrer."""

import pandas as pd
import pytest

from n2s.ingest.schema import SchemaInferrer, TableSchema


def test_infer_basic_types():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["alice", "bob", "charlie"],
            "price": [10.5, 20.0, 30.5],
        }
    )
    inferrer = SchemaInferrer()
    schema = inferrer.infer(df, table_name="products")

    assert schema.table_name == "products"
    assert len(schema.columns) == 3
    assert schema.columns[0].name == "id"
    assert schema.columns[0].sql_type == "INTEGER"
    assert schema.columns[1].name == "name"
    assert schema.columns[1].sql_type == "TEXT"
    assert schema.columns[2].name == "price"
    assert schema.columns[2].sql_type == "REAL"


def test_chinese_column_names_converted_to_pinyin():
    df = pd.DataFrame(
        {
            "订单号": [1, 2],
            "商品名称": ["item_a", "item_b"],
            "金额": [10.0, 20.0],
        }
    )
    inferrer = SchemaInferrer()
    schema = inferrer.infer(df, table_name="orders")

    names = [c.name for c in schema.columns]
    assert "dingdanhao" in names or "dingdan_hao" in names
    assert "shangpinmingcheng" in names or "shangpin_mingcheng" in names
    assert "jine" in names

    # Original Chinese names preserved as comments
    assert any(c.original_name == "订单号" for c in schema.columns)


def test_special_characters_replaced():
    df = pd.DataFrame(
        {
            "user-id": [1],
            "price$": [10.0],
            "name!": ["test"],
        }
    )
    inferrer = SchemaInferrer()
    schema = inferrer.infer(df, table_name="t")

    names = [c.name for c in schema.columns]
    assert "user_id" in names
    assert "price_" in names
    assert "name_" in names


def test_duplicate_names_after_cleanup():
    df = pd.DataFrame(
        {
            "用户": [1, 2],
            "客\u6237": [3, 4],  # Both map to "yonghu" after pinyin
        }
    )
    inferrer = SchemaInferrer()
    schema = inferrer.infer(df, table_name="t")

    names = [c.name for c in schema.columns]
    assert len(names) == 2
    assert names[0] != names[1]  # no collision
