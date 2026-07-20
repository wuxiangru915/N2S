"""FastAPI routes for data ingestion."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .engine import DataIngestor


class IngestDirectoryRequest(BaseModel):
    dir_path: str
    db_url: Optional[str] = None
    mode: str = "replace"


class IngestFileRequest(BaseModel):
    file_path: str
    table_name: Optional[str] = None
    db_url: Optional[str] = None
    mode: str = "replace"


# Global task registry (simple dict for single-process mode)
_tasks: dict[str, DataIngestor] = {}


def register_ingest_routes(
    app: FastAPI,
    default_db_url: str,
    llm_service=None,
    db_manager=None,
) -> None:
    """Register ingestion routes on the FastAPI app.

    Args:
        app: FastAPI application.
        default_db_url: SQLAlchemy URL for the default database (Agent's DB).
        llm_service: Optional LLM service for schema enhancement.
        db_manager: Optional DatabaseManager; when provided, routes use the
            active database URL dynamically instead of the static default_db_url.
    """

    def _resolve_db_url(request_db_url: Optional[str]) -> str:
        if request_db_url:
            return request_db_url
        if db_manager:
            return db_manager.get_active_url()
        return default_db_url

    @app.post("/api/ingest/directory")
    async def ingest_directory(request: IngestDirectoryRequest):
        db_url = _resolve_db_url(request.db_url)
        ingestor = DataIngestor(db_url=db_url, llm_service=llm_service)
        task_id = str(uuid.uuid4())[:8]
        _tasks[task_id] = ingestor

        # Run ingestion
        result = await ingestor.ingest_directory(request.dir_path, mode=request.mode)
        return {
            "task_id": task_id,
            "total_files": result.total_files,
            "succeeded": result.succeeded,
            "failed": result.failed,
            "tables_created": result.tables_created,
            "errors": result.errors,
        }

    @app.post("/api/ingest/file")
    async def ingest_file(request: IngestFileRequest):
        db_url = _resolve_db_url(request.db_url)
        ingestor = DataIngestor(db_url=db_url, llm_service=llm_service)
        task_id = str(uuid.uuid4())[:8]
        _tasks[task_id] = ingestor

        result = await ingestor.ingest_file(
            request.file_path,
            table_name=request.table_name,
            mode=request.mode,
        )
        return result.to_dict()

    @app.get("/api/ingest/progress/{task_id}")
    async def get_progress(task_id: str):
        if task_id not in _tasks:
            return {"error": "Task not found", "task_id": task_id}
        return _tasks[task_id].get_progress().to_dict()

    @app.get("/api/ingest/tables")
    async def list_tables():
        # Use the active DB to list tables
        db_url = _resolve_db_url(None)
        ingestor = DataIngestor(db_url=db_url, llm_service=None)
        tables = ingestor.list_tables()
        return [ingestor.get_table_info(t) for t in tables]
