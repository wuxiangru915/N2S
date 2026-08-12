"""N2S demo agent factory."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from n2s import Agent, AgentConfig
from n2s.core.registry import ToolRegistry
from n2s.core.user import RequestContext, User, UserResolver
from n2s.demo.data import demo_db_path
from n2s.demo.tools import ExplainSchemaTool
from n2s.integrations.local.agent_memory import DemoAgentMemory
from n2s.integrations.local import LocalFileSystem
from n2s.integrations.mock import MockLlmService
from n2s.integrations.sqlalchemy_runner import SqlAlchemyRunner
from n2s.tools import RunSqlTool, VisualizeDataTool

if TYPE_CHECKING:
    from n2s.core.llm import LlmService


class DemoUserResolver(UserResolver):
    """Maps every request to a single demo user."""

    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(
            id="demo-user",
            username="demo",
            email="demo@example.com",
            group_memberships=["all_users"],
        )


def _create_llm_service(provider: str | None = None) -> "LlmService":
    """Create an LLM service based on the requested provider.

    Supported providers:
      - mock    (default; deterministic mock, no API key needed)
      - agnes   (OpenAI-compatible endpoint; requires AGNES_API_KEY, AGNES_BASE_URL)
      - openai   (requires OPENAI_API_KEY)
      - anthropic (requires ANTHROPIC_API_KEY)
      - ollama   (requires local Ollama server)
      - mimo     (OpenAI-compatible endpoint; requires MIMO_API_KEY, MIMO_MODEL, MIMO_BASE_URL)
    """
    provider = (provider or os.getenv("N2S_LLM_PROVIDER", "mock")).lower().strip()

    if provider == "agnes":
        from n2s.integrations.openai import OpenAILlmService

        return OpenAILlmService(
            model=os.getenv("AGNES_MODEL", "agnes-2.0-flash"),
            api_key=os.getenv("AGNES_API_KEY"),
            base_url=os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
        )

    if provider == "openai":
        from n2s.integrations.openai import OpenAILlmService

        return OpenAILlmService(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    if provider == "anthropic":
        from n2s.integrations.anthropic import AnthropicLlmService

        return AnthropicLlmService(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        )

    if provider == "ollama":
        from n2s.integrations.ollama import OllamaLlmService

        return OllamaLlmService(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        )

    if provider == "mimo":
        from n2s.integrations.openai import OpenAILlmService

        return OpenAILlmService(
            model=os.getenv("MIMO_MODEL", "mimo-v2.5-pro"),
            api_key=os.getenv("MIMO_API_KEY"),
            base_url=os.getenv(
                "MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1"
            ),
        )

    if provider == "gemini":
        from n2s.integrations.google import GeminiLlmService

        return GeminiLlmService(
            model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    if provider == "mock":
        # Canned SQL mode: lets the key-less demo exercise the full agent loop
        # (tool call -> SQL execution -> final answer) against the bundled
        # demo database (employees table).
        return MockLlmService(
            response_content=(
                "N2S is running! This is a mock response. "
                "Set N2S_LLM_PROVIDER=agnes (or openai/anthropic/gemini/ollama) to use a real LLM."
            ),
            canned_sql={
                "多少条": "SELECT COUNT(*) AS total_count FROM employees",
                "多少行": "SELECT COUNT(*) AS total_count FROM employees",
                "员工总数": "SELECT COUNT(*) AS total_count FROM employees",
                "部门": (
                    "SELECT department, COUNT(*) AS cnt, AVG(salary) AS avg_salary "
                    "FROM employees GROUP BY department ORDER BY avg_salary DESC"
                ),
                "工资": (
                    "SELECT name, department, salary FROM employees "
                    "ORDER BY salary DESC"
                ),
                "员工列表": "SELECT id, name, department, salary FROM employees ORDER BY id",
            },
            final_answer=(
                "以上为 Mock 模式基于预置 SQL 的示例回答（查询已针对默认 demo 库 employees 表执行）。"
                "设置 N2S_LLM_PROVIDER=agnes（或 openai/anthropic/gemini/ollama）后即可用真实 LLM 回答任意自然语言问题。"
            ),
        )

    # Fallback: use mock
    return MockLlmService(
        response_content=(
            "N2S is running! This is a mock response. "
            "Set N2S_LLM_PROVIDER=agnes (or openai/anthropic/gemini/ollama) to use a real LLM."
        )
    )


def create_demo_agent(
    db_path: str | None = None,
    db_url: str | None = None,
    llm_provider: str | None = None,
) -> Agent:
    """Create a fully configured N2S demo agent.

    Args:
        db_path: Path to the SQLite database. Defaults to ``N2S_DEMO_DB`` env var or
            ``src/n2s/demo/n2s_demo.db``. Ignored if ``db_url`` is provided.
        db_url: SQLAlchemy connection URL (takes priority over ``db_path``).
            Supports SQLite, MySQL, PostgreSQL, etc.
        llm_provider: LLM provider to use. Defaults to ``N2S_LLM_PROVIDER`` env var or ``mock``.

    Returns:
        Configured ``Agent`` instance.
    """
    # Resolve the database URL
    if db_url:
        resolved_url = db_url
    else:
        db_path = db_path or os.getenv("N2S_DEMO_DB", str(demo_db_path()))
        resolved_url = f"sqlite:///{db_path}"

    llm_provider = llm_provider or os.getenv("N2S_LLM_PROVIDER", "mock")
    llm = _create_llm_service(llm_provider)
    file_system = LocalFileSystem(working_directory="./n2s_demo_data")

    tools = ToolRegistry()
    tools.register_local_tool(
        RunSqlTool(
            sql_runner=SqlAlchemyRunner(db_url=resolved_url),
            file_system=file_system,
        ),
        access_groups=[],
    )
    tools.register_local_tool(
        ExplainSchemaTool(db_url=resolved_url),
        access_groups=[],
    )
    tools.register_local_tool(
        VisualizeDataTool(file_system=file_system),
        access_groups=[],
    )

    return Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=DemoUserResolver(),
        agent_memory=DemoAgentMemory(),
        config=AgentConfig(stream_responses=True),
    )
