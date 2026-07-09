"""LLM schema enhancer: uses LLM to generate semantic table/column names."""

from __future__ import annotations

import asyncio
import json
import logging
from inspect import isawaitable

import pandas as pd

from .schema import ColumnSchema, TableSchema

logger = logging.getLogger(__name__)


class LlmSchemaEnhancer:
    """Enhances table schema using LLM-generated semantic names.

    When the LLM is unavailable or returns invalid output, silently
    degrades to the original schema.
    """

    def __init__(self, llm_service=None):
        """Initialize with an optional LLM service.

        Args:
            llm_service: LLM service with a `complete` method. If None,
                         enhancement is skipped entirely.
        """
        self._llm = llm_service

    def enhance(self, schema: TableSchema, df: pd.DataFrame) -> TableSchema:
        """Attempt to enhance a schema using the LLM.

        Args:
            schema: The rule-based inferred schema.
            df: Source DataFrame (used for sample data).

        Returns:
            Enhanced TableSchema, or the original if LLM is unavailable
            or returns invalid output.
        """
        if self._llm is None:
            return schema

        prompt = self._build_prompt(schema, df)

        try:
            response = self._llm.complete(prompt)
            # Support both sync and async LLM services
            if isawaitable(response):
                response = asyncio.run(response)
            content = getattr(response, "content", str(response))
            return self._parse_response(content, schema)
        except Exception as e:
            logger.warning("LLM enhancement failed, degrading to base schema: %s", e)
            return schema

    def _build_prompt(self, schema: TableSchema, df: pd.DataFrame) -> str:
        """Build the LLM prompt with sample data and current schema."""
        sample = df.head(5).to_string()
        columns_info = "\n".join(
            f"  - {c.name} ({c.sql_type}) [original: {c.original_name}]"
            for c in schema.columns
        )

        return f"""You are a database schema designer. Given the following sample data and inferred column names, suggest better SQL-friendly table and column names.

Table name: {schema.table_name}
Columns:
{columns_info}

Sample data (first 5 rows):
{sample}

Return ONLY a JSON object with this exact format:
{{
  "table_name": "suggested_table_name",
  "columns": [
    {{"name": "suggested_column_name", "comment": "Chinese description"}}
  ]
}}

Rules:
- Use snake_case for all names
- Names should be in English
- Keep names short but descriptive
- The number of columns must match the input
"""

    def _parse_response(self, content: str, base: TableSchema) -> TableSchema:
        """Parse LLM response and build enhanced schema, or return base on failure."""
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            logger.warning("LLM returned invalid JSON, degrading to base schema")
            return base

        if "table_name" not in data or "columns" not in data:
            logger.warning("LLM JSON missing required fields, degrading")
            return base

        llm_columns = data["columns"]
        if len(llm_columns) != len(base.columns):
            logger.warning("LLM column count mismatch, degrading")
            return base

        enhanced_columns: list[ColumnSchema] = []
        for base_col, llm_col in zip(base.columns, llm_columns):
            name = llm_col.get("name", base_col.name)
            comment = llm_col.get("comment", base_col.comment)
            enhanced_columns.append(
                ColumnSchema(
                    name=name,
                    original_name=base_col.original_name,
                    sql_type=base_col.sql_type,
                    comment=comment,
                )
            )

        return TableSchema(
            table_name=data["table_name"],
            columns=enhanced_columns,
        )
