"""
SQLAlchemy runner integration.

This module provides a generic SQL runner that works with any
SQLAlchemy-supported database (SQLite, MySQL, PostgreSQL, etc.).
"""

from .sql_runner import SqlAlchemyRunner

__all__ = ["SqlAlchemyRunner"]
