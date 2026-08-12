"""FastAPI server factory for the N2S demo."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from n2s.demo.agent import create_demo_agent
from n2s.demo.data import init_demo_db
from n2s.demo.database_manager import DatabaseManager
from n2s.demo.db_routes import register_database_routes
from n2s.ingest.routes import register_ingest_routes
from n2s.servers.base import ChatHandler
from n2s.servers.fastapi.routes import register_chat_routes


FRONTEND_DIST = (
    Path(__file__).resolve().parents[3] / "frontends" / "webcomponent" / "dist"
)


def create_demo_app() -> FastAPI:
    """Create and configure a FastAPI app with the N2S demo agent."""
    db_path = init_demo_db()
    default_db_url = f"sqlite:///{db_path}"

    # Set up database manager with the default SQLite database
    db_manager = DatabaseManager()
    db_manager.ensure_default(default_db_url)

    # Create agent using the active database
    active_url = db_manager.get_active_url()
    agent = create_demo_agent(db_url=active_url)

    app = FastAPI(title="N2S Demo", description="Natural-to-SQL Agent demo")

    # Serve built frontend assets if available; otherwise fall back to the
    # CDN build so the demo UI works out of the box (the frontend dist is
    # built separately and is not committed to the repository).
    has_frontend = FRONTEND_DIST.exists()
    if has_frontend:
        app.mount("/static", StaticFiles(directory=str(FRONTEND_DIST)), name="static")

    config = {"dev_mode": has_frontend, "static_path": "/static"}

    @app.get("/health")
    async def health():
        """Health check endpoint (listed in the demo UI)."""
        active = db_manager.get_active()
        return {"status": "ok", "database": (active or {}).get("name", "none")}

    chat_handler = ChatHandler(agent)
    register_chat_routes(app, chat_handler, config=config)

    # Register data ingestion routes (uses active database dynamically)
    register_ingest_routes(
        app,
        default_db_url=active_url,
        llm_service=agent.llm_service,
        db_manager=db_manager,
    )

    # Register database management routes (switching recreates the agent)
    register_database_routes(app, db_manager, chat_handler)

    return app
