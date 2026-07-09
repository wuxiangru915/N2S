"""Generic SQLAlchemy implementation of SqlRunner interface."""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from n2s.capabilities.sql_runner import SqlRunner, RunSqlToolArgs
from n2s.core.tool import ToolContext


class SqlAlchemyRunner(SqlRunner):
    """Generic SqlRunner backed by a SQLAlchemy engine.

    Works with any SQLAlchemy-supported database URL:
      - sqlite:///path/to/db.sqlite
      - mysql+pymysql://user:pass@host:port/dbname
      - postgresql://user:pass@host:port/dbname
    """

    def __init__(self, db_url: str):
        """Initialize with a SQLAlchemy connection URL.

        Args:
            db_url: SQLAlchemy connection URL.
        """
        self.db_url = db_url
        self._engine: Engine = create_engine(db_url)

    async def run_sql(self, args: RunSqlToolArgs, context: ToolContext) -> pd.DataFrame:
        """Execute SQL query and return results as a DataFrame.

        Args:
            args: SQL query arguments.
            context: Tool execution context.

        Returns:
            DataFrame with query results (SELECT) or rows-affected count.
        """
        query_type = args.sql.strip().upper().split()[0]

        with self._engine.connect() as conn:
            result = conn.execute(text(args.sql))

            if query_type == "SELECT":
                rows = result.fetchall()
                if not rows:
                    return pd.DataFrame()
                return pd.DataFrame(rows, columns=result.keys())
            else:
                conn.commit()
                rows_affected = result.rowcount
                return pd.DataFrame({"rows_affected": [rows_affected]})
