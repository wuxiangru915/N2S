"""
Mock LLM service implementation for testing and key-less demos.

This module provides a simple implementation of the LlmService interface,
useful for testing and development without requiring actual LLM API calls.

Besides the static-text mode (default), it supports a *canned SQL* mode:
map question keywords to SQL queries so the demo can exercise the full
agent loop (tool call -> SQL execution -> final answer) without an API key.
"""

import asyncio
from typing import AsyncGenerator, Dict, List, Optional

from n2s.core.llm import LlmService, LlmRequest, LlmResponse, LlmStreamChunk
from n2s.core.tool import ToolCall, ToolSchema


class MockLlmService(LlmService):
    """Mock LLM service that returns predefined responses.

    Modes:
      - Static text (default): returns ``response_content`` on every request.
      - Canned SQL: when ``canned_sql`` maps a keyword to a SQL statement and
        the user message contains that keyword, the mock returns a ``run_sql``
        tool call. Once the tool result is present in the conversation, it
        returns the final answer (``final_answer`` or ``response_content``).

    Note: canned SQL targets the default demo database (``employees``).
    Switch ``N2S_LLM_PROVIDER`` to a real LLM to answer arbitrary questions.
    """

    def __init__(
        self,
        response_content: str = "Hello! This is a mock response.",
        canned_sql: Optional[Dict[str, str]] = None,
        final_answer: Optional[str] = None,
    ):
        self.response_content = response_content
        self.canned_sql = canned_sql or {}
        self.final_answer = final_answer
        self.call_count = 0

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #
    def _latest_user_message(self, request: LlmRequest) -> str:
        for message in reversed(request.messages):
            if message.role == "user":
                return message.content or ""
        return ""

    def _has_tool_results(self, request: LlmRequest) -> bool:
        return any(message.role == "tool" for message in request.messages)

    def _match_sql(self, text: str) -> Optional[str]:
        lowered = text.lower()
        for keyword, sql in self.canned_sql.items():
            if keyword.lower() in lowered:
                return sql
        return None

    def _build_tool_call_response(self, sql: str) -> LlmResponse:
        """Return a response requesting a run_sql tool call."""
        self.call_count += 1
        return LlmResponse(
            content="我将执行查询来完成你的问题。",
            tool_calls=[
                ToolCall(
                    id=f"mock_sql_{self.call_count}",
                    name="run_sql",
                    arguments={"sql": sql},
                )
            ],
            finish_reason="tool_calls",
            usage={"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
        )

    def _build_final_response(self, suffix: str = "") -> LlmResponse:
        """Return the final textual answer."""
        answer = self.final_answer or self.response_content
        return LlmResponse(
            content=f"{answer} (Request #{self.call_count}){suffix}",
            finish_reason="stop",
            usage={"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
        )

    # ------------------------------------------------------------------ #
    # LlmService interface
    # ------------------------------------------------------------------ #
    async def send_request(self, request: LlmRequest) -> LlmResponse:
        """Send a request to the mock LLM."""
        await asyncio.sleep(0.1)

        if self.canned_sql:
            if self._has_tool_results(request):
                return self._build_final_response()
            sql = self._match_sql(self._latest_user_message(request))
            if sql:
                return self._build_tool_call_response(sql)

        self.call_count += 1
        # Static mode: return the configured response.
        return LlmResponse(
            content=f"{self.response_content} (Request #{self.call_count})",
            finish_reason="stop",
            usage={"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
        )

    async def stream_request(
        self, request: LlmRequest
    ) -> AsyncGenerator[LlmStreamChunk, None]:
        """Stream a request to the mock LLM."""
        if self.canned_sql:
            if self._has_tool_results(request):
                # Final answer: stream the text word by word.
                answer = (self.final_answer or self.response_content).split()
                for i, word in enumerate(answer):
                    await asyncio.sleep(0.02)
                    yield LlmStreamChunk(
                        content=word + (" " if i < len(answer) - 1 else ""),
                        finish_reason="stop" if i == len(answer) - 1 else None,
                    )
                return
            sql = self._match_sql(self._latest_user_message(request))
            if sql:
                # Emit the tool call in a single chunk.
                self.call_count += 1
                yield LlmStreamChunk(
                    tool_calls=[
                        ToolCall(
                            id=f"mock_sql_{self.call_count}",
                            name="run_sql",
                            arguments={"sql": sql},
                        )
                    ],
                    finish_reason="tool_calls",
                )
                return

        self.call_count += 1
        # Static mode: stream the configured response.
        words = f"{self.response_content} (Streamed #{self.call_count})".split()
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate streaming delay
            chunk_content = word + (" " if i < len(words) - 1 else "")
            yield LlmStreamChunk(
                content=chunk_content,
                finish_reason="stop" if i == len(words) - 1 else None,
            )

    async def validate_tools(self, tools: List[ToolSchema]) -> List[str]:
        """Validate tool schemas and return any errors."""
        # Mock validation - no errors
        return []

    def set_response(self, content: str) -> None:
        """Set the response content for testing."""
        self.response_content = content

    def set_canned_sql(self, canned_sql: Dict[str, str]) -> None:
        """Set the keyword -> SQL mapping used for canned tool calls."""
        self.canned_sql = canned_sql

    def reset_call_count(self) -> None:
        """Reset the counter and tool-call state."""
        self.call_count = 0
