"""Data ingestion pipeline for N2S.

Scans directories for data files, auto-creates tables, and loads data
into the target database for NL2SQL querying.
"""

from .models import IngestResult, IngestProgress, FileProgress
from .engine import DataIngestor

__all__ = [
    "DataIngestor",
    "IngestResult",
    "IngestProgress",
    "FileProgress",
]
