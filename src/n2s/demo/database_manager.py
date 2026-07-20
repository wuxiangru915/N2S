"""Database connection manager for multi-database support."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DatabaseConfig:
    """Configuration for a single database connection."""

    name: str
    db_type: str  # "sqlite", "mysql", "postgresql"
    db_url: str
    host: str = ""
    port: int = 0
    database: str = ""
    username: str = ""
    is_active: bool = False
    is_default: bool = False  # default DB cannot be deleted

    def to_dict(self) -> dict:
        """Serialize to dict (password excluded)."""
        d = asdict(self)
        return d

    def to_safe_dict(self) -> dict:
        """Serialize to dict without sensitive fields."""
        d = asdict(self)
        # db_url may contain password; keep it for internal use but not in listing
        return d


class DatabaseManager:
    """Manage multiple database connections with persistence.

    Stores configs in a JSON file. The default SQLite database is always
    present and cannot be removed.
    """

    def __init__(self, config_dir: str = "n2s_demo_data"):
        self._config_dir = Path(config_dir)
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_path = self._config_dir / "databases.json"
        self._databases: list[DatabaseConfig] = []
        self._load()

    def _load(self) -> None:
        """Load configs from JSON file, or initialize with default SQLite."""
        if self._config_path.exists():
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._databases = [DatabaseConfig(**item) for item in data]
        else:
            self._databases = []

    def _save(self) -> None:
        """Persist configs to JSON file."""
        data = [asdict(db) for db in self._databases]
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def ensure_default(self, db_url: str) -> None:
        """Ensure the default SQLite database exists in the list.

        Args:
            db_url: SQLAlchemy URL for the default SQLite database.
        """
        for db in self._databases:
            if db.is_default:
                # Update URL in case path changed
                db.db_url = db_url
                if not self._any_active():
                    db.is_active = True
                self._save()
                return

        self._databases.append(
            DatabaseConfig(
                name="default",
                db_type="sqlite",
                db_url=db_url,
                is_active=not self._any_active(),
                is_default=True,
            )
        )
        self._save()

    def _any_active(self) -> bool:
        return any(db.is_active for db in self._databases)

    def list_databases(self) -> list[dict]:
        """Return all database configs as dicts."""
        return [db.to_safe_dict() for db in self._databases]

    def add_database(
        self,
        name: str,
        db_type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
    ) -> dict:
        """Add a new database connection.

        Returns:
            The created database config as dict.
        """
        # Check name uniqueness
        if any(db.name == name for db in self._databases):
            raise ValueError(f"Database '{name}' already exists")

        # Construct SQLAlchemy URL
        db_url = self._build_url(db_type, host, port, database, username, password)

        config = DatabaseConfig(
            name=name,
            db_type=db_type,
            db_url=db_url,
            host=host,
            port=port,
            database=database,
            username=username,
        )
        self._databases.append(config)
        self._save()
        return config.to_safe_dict()

    def _build_url(
        self,
        db_type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
    ) -> str:
        """Build a SQLAlchemy connection URL from components."""
        if db_type == "mysql":
            driver = "mysql+pymysql"
            port = port or 3306
        elif db_type == "postgresql":
            driver = "postgresql"
            port = port or 5432
        elif db_type == "sqlite":
            return f"sqlite:///{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        url = f"{driver}://{username}:{password}@{host}:{port}/{database}"
        return url

    def remove_database(self, name: str) -> bool:
        """Remove a database connection. Default DB cannot be removed."""
        for i, db in enumerate(self._databases):
            if db.name == name:
                if db.is_default:
                    raise ValueError("Cannot remove the default database")
                if db.is_active:
                    # Activate the default instead
                    for d in self._databases:
                        if d.is_default:
                            d.is_active = True
                del self._databases[i]
                self._save()
                return True
        return False

    def get_active(self) -> Optional[dict]:
        """Return the active database config as dict."""
        for db in self._databases:
            if db.is_active:
                return db.to_safe_dict()
        return None

    def get_active_url(self) -> str:
        """Return the SQLAlchemy URL of the active database."""
        for db in self._databases:
            if db.is_active:
                return db.db_url
        # Fallback: return first database
        if self._databases:
            return self._databases[0].db_url
        raise RuntimeError("No databases configured")

    def set_active(self, name: str) -> dict:
        """Set the active database by name.

        Returns:
            The newly active database config as dict.
        """
        found = False
        for db in self._databases:
            if db.name == name:
                db.is_active = True
                found = True
            else:
                db.is_active = False

        if not found:
            raise ValueError(f"Database '{name}' not found")

        self._save()
        return self.get_active()

    def test_connection(self, db_url: str) -> tuple[bool, str]:
        """Test a database connection.

        Returns:
            Tuple of (success, message).
        """
        try:
            from sqlalchemy import create_engine, text

            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine.dispose()
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
