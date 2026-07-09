"""Schema introspection tool for the N2S demo."""

from __future__ import annotations

from typing import Type

import sqlalchemy
from pydantic import BaseModel, Field
from sqlalchemy import inspect as sa_inspect

from n2s.components import (
    UiComponent,
    SimpleTextComponent,
    RichTextComponent,
    ComponentType,
)
from n2s.core.tool import Tool, ToolContext, ToolResult


class ExplainSchemaToolArgs(BaseModel):
    """Arguments for the schema explanation tool."""

    tables: list[str] | None = Field(
        default=None,
        description=(
            "Optional list of table names to describe. "
            "If omitted, all tables in the database are returned."
        ),
    )


class ExplainSchemaTool(Tool[ExplainSchemaToolArgs]):
    """Return the schema (tables and columns) of the database.

    Uses SQLAlchemy inspect() for dialect-aware introspection,
    supporting SQLite, DuckDB, MySQL, PostgreSQL, SQL Server, etc.
    """

    def __init__(self, database_path: str | None = None, db_url: str | None = None):
        """Initialize with either a SQLite file path or a SQLAlchemy URL.

        Args:
            database_path: Path to SQLite database file (backward compat).
            db_url: SQLAlchemy connection URL (takes priority over database_path).
        """
        if db_url:
            self._engine = sqlalchemy.create_engine(db_url)
        elif database_path:
            self._engine = sqlalchemy.create_engine(f"sqlite:///{database_path}")
        else:
            raise ValueError("Either database_path or db_url must be provided")

    @property
    def name(self) -> str:
        return "explain_schema"

    @property
    def description(self) -> str:
        return (
            "Describe the database schema: list tables and their columns, "
            "data types, and primary keys. Use this BEFORE writing SQL to understand "
            "what data is available."
        )

    def get_args_schema(self) -> Type[ExplainSchemaToolArgs]:
        return ExplainSchemaToolArgs

    async def execute(
        self, context: ToolContext, args: ExplainSchemaToolArgs
    ) -> ToolResult:
        try:
            inspector = sa_inspect(self._engine)

            if args.tables:
                tables = args.tables
            else:
                tables = inspector.get_table_names()
                tables.sort()

            lines = []
            for table in tables:
                columns = inspector.get_columns(table)
                pk = inspector.get_pk_constraint(table)
                pk_cols = set(pk.get("constrained_columns", []))

                col_lines = [
                    f"  - {col['name']} ({col['type']})"
                    + (" PRIMARY KEY" if col["name"] in pk_cols else "")
                    + (" NOT NULL" if col.get("nullable") is False else "")
                    for col in columns
                ]
                lines.append(f"Table: {table}")
                lines.extend(col_lines)
                lines.append("")

            schema_text = "\n".join(lines).strip()

            return ToolResult(
                success=True,
                result_for_llm=schema_text,
                ui_component=UiComponent(
                    rich_component=RichTextComponent(
                        type=ComponentType.TEXT,
                        content=schema_text,
                    ),
                    simple_component=SimpleTextComponent(text=schema_text),
                ),
                metadata={"tables": tables},
            )
        except Exception as e:
            error_message = f"Error reading schema: {str(e)}"
            return ToolResult(
                success=False,
                result_for_llm=error_message,
                ui_component=UiComponent(
                    rich_component=RichTextComponent(
                        type=ComponentType.RICH_TEXT,
                        content=error_message,
                    ),
                    simple_component=SimpleTextComponent(text=error_message),
                ),
                error=str(e),
            )
