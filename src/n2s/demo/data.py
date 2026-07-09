"""Demo database initialization for N2S."""

import sqlite3
from pathlib import Path


DEFAULT_DB_NAME = "n2s_demo.db"


def demo_db_path() -> Path:
    """Return the default path for the demo SQLite database."""
    return Path(__file__).resolve().parent / DEFAULT_DB_NAME


def init_demo_db(db_path: Path | str | None = None) -> Path:
    """Create (or reset) the demo SQLite database with sample employee data.

    Args:
        db_path: Path to the SQLite file. Defaults to ``src/n2s/demo/n2s_demo.db``.

    Returns:
        The absolute path to the created database file.
    """
    db_path = Path(db_path) if db_path else demo_db_path()
    db_path = db_path.resolve()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER NOT NULL
        )
        """
    )
    cursor.execute("DELETE FROM employees")
    cursor.executemany(
        "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
        [
            ("Alice", "Engineering", 120000),
            ("Bob", "Sales", 80000),
            ("Charlie", "Engineering", 110000),
            ("Diana", "Marketing", 95000),
            ("Evan", "Sales", 85000),
            ("Fiona", "Engineering", 130000),
        ],
    )
    conn.commit()
    conn.close()
    return db_path
