"""File reader: reads data files into pandas DataFrames."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


class FileReader:
    """Reads supported data file formats into pandas DataFrames."""

    def read(self, file_path: str | Path, file_type: str) -> pd.DataFrame:
        """Read a data file into a DataFrame.

        Args:
            file_path: Path to the data file.
            file_type: One of: csv, excel, json, parquet.

        Returns:
            pandas DataFrame with the file contents.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file type is not supported.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_type == "csv":
            return self._read_csv(file_path)
        elif file_type == "excel":
            return self._read_excel(file_path)
        elif file_type == "json":
            return self._read_json(file_path)
        elif file_type == "parquet":
            return self._read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _read_csv(self, path: Path) -> pd.DataFrame:
        """Read CSV with UTF-8, fallback to GBK for Chinese Windows."""
        try:
            return pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding="gbk")

    def _read_excel(self, path: Path) -> pd.DataFrame:
        """Read .xls (xlrd) or .xlsx (openpyxl) — pandas auto-detects engine."""
        return pd.read_excel(path)

    def _read_json(self, path: Path) -> pd.DataFrame:
        """Read JSON file into DataFrame."""
        return pd.read_json(path)

    def _read_parquet(self, path: Path) -> pd.DataFrame:
        """Read Parquet file into DataFrame."""
        return pd.read_parquet(path)
