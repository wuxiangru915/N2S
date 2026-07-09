"""Data models for the ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FileProgress:
    """Progress tracking for a single file during ingestion."""

    filename: str
    stage: str = "pending"  # pending | reading | infering | ingesting | done | error
    error: str | None = None
    rows_loaded: int = 0
    table_name: str | None = None


@dataclass
class IngestProgress:
    """Overall progress for an ingestion task."""

    task_id: str
    total_files: int = 0
    completed: int = 0
    failed: int = 0
    files: list[FileProgress] = field(default_factory=list)
    status: str = "pending"  # pending | running | done | error

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON API responses."""
        return {
            "task_id": self.task_id,
            "total_files": self.total_files,
            "completed": self.completed,
            "failed": self.failed,
            "status": self.status,
            "files": [
                {
                    "filename": f.filename,
                    "stage": f.stage,
                    "error": f.error,
                    "rows_loaded": f.rows_loaded,
                    "table_name": f.table_name,
                }
                for f in self.files
            ],
        }


@dataclass
class IngestResult:
    """Final result of an ingestion operation."""

    success: bool
    total_files: int
    succeeded: int
    failed: int
    tables_created: list[str]
    errors: list[dict[str, str]]  # [{"filename": "...", "error": "..."}]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON API responses."""
        return {
            "success": self.success,
            "total_files": self.total_files,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "tables_created": self.tables_created,
            "errors": self.errors,
        }
