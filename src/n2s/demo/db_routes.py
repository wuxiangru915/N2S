"""FastAPI routes for database connection management."""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from n2s.demo.agent import create_demo_agent
from n2s.demo.database_manager import DatabaseManager
from n2s.servers.base import ChatHandler


class AddDatabaseRequest(BaseModel):
    name: str
    db_type: str  # "mysql", "postgresql"
    host: str = "localhost"
    port: int = 0
    database: str = ""
    username: str = ""
    password: str = ""


class SetActiveRequest(BaseModel):
    name: str


class TestConnectionRequest(BaseModel):
    db_type: str
    host: str = "localhost"
    port: int = 0
    database: str = ""
    username: str = ""
    password: str = ""


def register_database_routes(
    app: FastAPI,
    db_manager: DatabaseManager,
    chat_handler: ChatHandler,
    llm_provider: Optional[str] = None,
) -> None:
    """Register database management routes on the FastAPI app.

    Args:
        app: FastAPI application.
        db_manager: DatabaseManager instance for managing connections.
        chat_handler: ChatHandler whose agent will be swapped on DB switch.
        llm_provider: LLM provider string for agent recreation.
    """

    @app.get("/api/databases")
    async def list_databases():
        return db_manager.list_databases()

    @app.post("/api/databases")
    async def add_database(request: AddDatabaseRequest):
        try:
            config = db_manager.add_database(
                name=request.name,
                db_type=request.db_type,
                host=request.host,
                port=request.port,
                database=request.database,
                username=request.username,
                password=request.password,
            )
            return {"success": True, "database": config}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    @app.delete("/api/databases/{name}")
    async def remove_database(name: str):
        try:
            removed = db_manager.remove_database(name)
            if not removed:
                return {"success": False, "error": "Database not found"}
            # If the active DB was removed, recreate agent with new active
            active = db_manager.get_active()
            if active:
                new_agent = create_demo_agent(
                    db_url=active["db_url"], llm_provider=llm_provider
                )
                chat_handler.agent = new_agent
            return {"success": True}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    @app.put("/api/databases/active")
    async def set_active_database(request: SetActiveRequest):
        try:
            config = db_manager.set_active(request.name)
            # Recreate agent with the new database
            new_agent = create_demo_agent(
                db_url=config["db_url"], llm_provider=llm_provider
            )
            chat_handler.agent = new_agent
            return {"success": True, "database": config}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/databases/active")
    async def get_active_database():
        active = db_manager.get_active()
        if active:
            return active
        return {"error": "No active database"}

    @app.post("/api/databases/test")
    async def test_connection(request: TestConnectionRequest):
        # Build URL from components
        if request.db_type == "mysql":
            port = request.port or 3306
            db_url = f"mysql+pymysql://{request.username}:{request.password}@{request.host}:{port}/{request.database}"
        elif request.db_type == "postgresql":
            port = request.port or 5432
            db_url = f"postgresql://{request.username}:{request.password}@{request.host}:{port}/{request.database}"
        else:
            return {"success": False, "error": f"Unsupported type: {request.db_type}"}

        success, message = db_manager.test_connection(db_url)
        return {"success": success, "message": message}
