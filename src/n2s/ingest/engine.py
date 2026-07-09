"""DataIngestor: orchestrates the full ingestion pipeline."""

from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional

import pandas as pd

from .loader import DatabaseLoader
from .llm_enhancer import LlmSchemaEnhancer
from .models import FileProgress, IngestProgress, IngestResult
from .reader import FileReader
from .schema import SchemaInferrer
from .scanner import DirectoryScanner

logger = logging.getLogger(__name__)


class DataIngestor:
    """Orchestrates the data ingestion pipeline.

    Scans directories, reads files, infers schema, optionally enhances
    with LLM, and loads into the target database.
    """

    def __init__(self, db_url: str, llm_service=None):
        """Initialize the ingestor.

        Args:
            db_url: SQLAlchemy connection URL for the target database.
            llm_service: Optional LLM service for schema enhancement.
        """
        self.db_url = db_url
        self._scanner = DirectoryScanner()
        self._reader = FileReader()
        self._inferrer = SchemaInferrer()
        self._loader = DatabaseLoader(db_url)
        self._enhancer = LlmSchemaEnhancer(llm_service)
        self._progress: IngestProgress | None = None

    async def ingest_directory(
        self, dir_path: str, mode: str = "replace"
    ) -> IngestResult:
        """Scan and ingest all supported files from a directory.

        Args:
            dir_path: Path to the directory to scan.
            mode: Table exists behavior: replace, append, or fail.

        Returns:
            IngestResult with per-file status.
        """
        scan_result = self._scanner.scan(dir_path)

        task_id = str(uuid.uuid4())[:8]
        self._progress = IngestProgress(
            task_id=task_id,
            total_files=len(scan_result.files),
            status="running",
        )
        for f in scan_result.files:
            self._progress.files.append(
                FileProgress(filename=f.filename, table_name=f.table_name)
            )

        tables_created: list[str] = []
        errors: list[dict[str, str]] = []
        succeeded = 0

        for i, scanned_file in enumerate(scan_result.files):
            file_progress = self._progress.files[i]
            try:
                table_name = await self._ingest_one(scanned_file, mode, file_progress)
                tables_created.append(table_name)
                succeeded += 1
                self._progress.completed += 1
            except Exception as e:
                logger.error("Failed to ingest %s: %s", scanned_file.filename, e)
                file_progress.stage = "error"
                file_progress.error = str(e)
                errors.append({"filename": scanned_file.filename, "error": str(e)})
                self._progress.failed += 1

        self._progress.status = "done"

        return IngestResult(
            success=self._progress.failed == 0,
            total_files=len(scan_result.files),
            succeeded=succeeded,
            failed=self._progress.failed,
            tables_created=tables_created,
            errors=errors,
        )

    async def ingest_file(
        self,
        file_path: str,
        table_name: str | None = None,
        mode: str = "replace",
    ) -> IngestResult:
        """Ingest a single file.

        Args:
            file_path: Path to the data file.
            table_name: Optional table name override.
            mode: Table exists behavior.

        Returns:
            IngestResult.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        from .scanner import EXTENSION_MAP

        ext = path.suffix.lower()
        if ext not in EXTENSION_MAP:
            raise ValueError(f"Unsupported file type: {ext}")

        file_type = EXTENSION_MAP[ext]
        name = table_name or path.stem

        task_id = str(uuid.uuid4())[:8]
        self._progress = IngestProgress(
            task_id=task_id,
            total_files=1,
            status="running",
            files=[FileProgress(filename=path.name, table_name=name)],
        )

        file_progress = self._progress.files[0]

        # Build a lightweight ScannedFile-like object
        from .scanner import ScannedFile

        scanned = ScannedFile(
            path=path,
            filename=path.name,
            extension=ext,
            file_type=file_type,
            table_name=name,
        )

        try:
            table = await self._ingest_one(scanned, mode, file_progress)
            self._progress.completed = 1
            self._progress.status = "done"
            return IngestResult(
                success=True,
                total_files=1,
                succeeded=1,
                failed=0,
                tables_created=[table],
                errors=[],
            )
        except Exception as e:
            file_progress.stage = "error"
            file_progress.error = str(e)
            self._progress.failed = 1
            self._progress.status = "done"
            return IngestResult(
                success=False,
                total_files=1,
                succeeded=0,
                failed=1,
                tables_created=[],
                errors=[{"filename": path.name, "error": str(e)}],
            )

    async def _ingest_one(self, scanned_file, mode: str, file_progress: FileProgress) -> str:
        """Process a single file through the full pipeline. Returns table name."""
        # Stage: reading
        file_progress.stage = "reading"
        df = self._reader.read(scanned_file.path, scanned_file.file_type)

        if df.empty:
            file_progress.stage = "done"
            file_progress.rows_loaded = 0
            return scanned_file.table_name

        # Stage: inferring
        file_progress.stage = "infering"
        schema = self._inferrer.infer(df, scanned_file.table_name)

        # Stage: LLM enhancement (optional)
        schema = self._enhancer.enhance(schema, df)

        # Stage: ingesting
        file_progress.stage = "ingesting"
        rows = self._loader.load(df, schema, mode=mode)
        file_progress.rows_loaded = rows
        file_progress.stage = "done"
        return schema.table_name

    def get_progress(self) -> IngestProgress:
        """Return current ingestion progress."""
        if self._progress is None:
            return IngestProgress(task_id="", status="pending")
        return self._progress

    def list_tables(self) -> list[str]:
        """List tables in the target database."""
        return self._loader.list_tables()

    def get_table_info(self, table_name: str) -> dict:
        """Get info for a specific table."""
        return self._loader.get_table_info(table_name)

    # Synchronous wrappers for CLI and testing
    def ingest_directory_sync(self, dir_path: str, mode: str = "replace") -> IngestResult:
        """Sync wrapper for ingest_directory."""
        return asyncio.run(self.ingest_directory(dir_path, mode))

    def ingest_file_sync(
        self, file_path: str, table_name: str | None = None, mode: str = "replace"
    ) -> IngestResult:
        """Sync wrapper for ingest_file."""
        return asyncio.run(self.ingest_file(file_path, table_name, mode))
