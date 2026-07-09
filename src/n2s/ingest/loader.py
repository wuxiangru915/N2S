"""Database loader: writes DataFrames to the target database via SQLAlchemy."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import sqlalchemy
from sqlalchemy import inspect, text

from .schema import TableSchema


class DatabaseLoader:
    """Loads DataFrames into a database using pandas.to_sql()."""

    def __init__(self, db_url: str):
        """Initialize with a SQLAlchemy connection URL.

        Args:
            db_url: SQLAlchemy connection string (e.g. sqlite:///data.db)
        """
        self.db_url = db_url
        self._engine = sqlalchemy.create_engine(db_url)

    def load(
        self,
        df: pd.DataFrame,
        schema: TableSchema,
        mode: str = "replace",
    ) -> int:
        """Write a DataFrame to the database as a table.

        Args:
            df: Source DataFrame.
            schema: Inferred table schema (provides table name).
            mode: Table exists behavior: "replace", "append", or "fail".

        Returns:
            Number of rows written.

        Raises:
            ValueError: If mode is invalid.
        """
        if mode not in ("replace", "append", "fail"):
            raise ValueError(f"Invalid mode: {mode}. Use 'replace', 'append', or 'fail'.")

        if df.empty:
            return 0

        # Rename DataFrame columns to match cleaned schema names
        rename_map = {
            orig: col.name
            for orig, col in zip(df.columns, schema.columns)
        }
        df = df.rename(columns=rename_map)

        df.to_sql(
            schema.table_name,
            self._engine,
            if_exists=mode,
            index=False,
        )

        return len(df)

    def list_tables(self) -> list[str]:
        """List all tables in the database."""
        inspector = inspect(self._engine)
        return inspector.get_table_names()

    def get_table_info(self, table_name: str) -> dict:
        """Get column info and row count for a table."""
        inspector = inspect(self._engine)
        columns = inspector.get_columns(table_name)

        with self._engine.connect() as conn:
            result = conn.exec_driver_sql(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = result.fetchone()[0]

        return {
            "name": table_name,
            "columns": len(columns),
            "rows": row_count,
        }

    def close(self):
        """Dispose of the SQLAlchemy engine."""
        self._engine.dispose()
