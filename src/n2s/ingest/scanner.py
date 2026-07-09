"""Directory scanner for data files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Supported file extensions mapped to file types
EXTENSION_MAP: dict[str, str] = {
    ".csv": "csv",
    ".xls": "excel",
    ".xlsx": "excel",
    ".json": "json",
    ".parquet": "parquet",
    ".db": "sqlite_db",
    ".sqlite": "sqlite_db",
    ".sqlite3": "sqlite_db",
}


@dataclass
class ScannedFile:
    """A single data file found during scanning."""

    path: Path
    filename: str
    extension: str
    file_type: str  # csv | excel | json | parquet | sqlite_db
    table_name: str


@dataclass
class ScanResult:
    """Result of a directory scan."""

    files: list[ScannedFile] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


class DirectoryScanner:
    """Scans a directory for supported data files."""

    def scan(self, dir_path: str | Path) -> ScanResult:
        """Walk a directory and classify all supported data files.

        Args:
            dir_path: Path to the directory to scan.

        Returns:
            ScanResult with found files and skipped files.

        Raises:
            FileNotFoundError: If the directory does not exist.
            NotADirectoryError: If the path is not a directory.
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        result = ScanResult()

        for entry in sorted(dir_path.iterdir()):
            if entry.is_dir():
                continue

            ext = entry.suffix.lower()

            if ext in EXTENSION_MAP:
                file_type = EXTENSION_MAP[ext]
                table_name = entry.stem  # filename without extension
                result.files.append(
                    ScannedFile(
                        path=entry,
                        filename=entry.name,
                        extension=ext,
                        file_type=file_type,
                        table_name=table_name,
                    )
                )
            else:
                result.skipped.append(entry)

        return result
