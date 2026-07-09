"""Schema inferrer: type inference, column name cleanup, DDL generation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

try:
    from pypinyin import lazy_pinyin
    _HAS_PYPINYIN = True
except ImportError:
    _HAS_PYPINYIN = False


@dataclass
class ColumnSchema:
    """Schema for a single column."""

    name: str  # cleaned, SQL-safe name
    original_name: str  # original column name from source file
    sql_type: str  # INTEGER | TEXT | REAL | BLOB
    comment: str | None = None


@dataclass
class TableSchema:
    """Schema for a database table."""

    table_name: str
    columns: list[ColumnSchema] = field(default_factory=list)


class SchemaInferrer:
    """Infers SQL schema from a pandas DataFrame."""

    # pandas dtype -> SQLite type mapping (SQLite is the default target)
    DTYPE_MAP: dict[str, str] = {
        "int64": "INTEGER",
        "int32": "INTEGER",
        "float64": "REAL",
        "float32": "REAL",
        "bool": "INTEGER",
        "object": "TEXT",
        "datetime64[ns]": "TEXT",
    }

    def infer(self, df: pd.DataFrame, table_name: str) -> TableSchema:
        """Infer table schema from a DataFrame.

        Args:
            df: Source DataFrame.
            table_name: Target table name.

        Returns:
            TableSchema with cleaned column names and SQL types.
        """
        table_name = self._clean_name(table_name)
        columns: list[ColumnSchema] = []
        seen_names: set[str] = set()

        for orig_name in df.columns:
            clean = self._clean_name(str(orig_name))
            # Handle duplicate names after cleanup
            base = clean
            counter = 2
            while clean in seen_names:
                clean = f"{base}_{counter}"
                counter += 1
            seen_names.add(clean)

            sql_type = self._infer_type(df[orig_name])
            comment = str(orig_name) if str(orig_name) != clean else None

            columns.append(
                ColumnSchema(
                    name=clean,
                    original_name=str(orig_name),
                    sql_type=sql_type,
                    comment=comment,
                )
            )

        return TableSchema(table_name=table_name, columns=columns)

    def _clean_name(self, name: str) -> str:
        """Clean a column or table name for SQL safety.

        - Convert Chinese characters to pinyin
        - Replace special characters with underscores
        - Lowercase
        """
        name = str(name).strip().lower()

        if _HAS_PYPINYIN:
            # Convert Chinese chars to pinyin, keep ASCII as-is
            parts = lazy_pinyin(name)
            name = "".join(parts)

        # Replace any non-alphanumeric character with underscore
        name = re.sub(r"[^a-z0-9]+", "_", name)
        # Ensure not empty
        if not name:
            name = "column"
        return name

    def _infer_type(self, series: pd.Series) -> str:
        """Map pandas dtype to SQL type string."""
        dtype_str = str(series.dtype)
        return self.DTYPE_MAP.get(dtype_str, "TEXT")
