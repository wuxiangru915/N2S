"""Middleware for capturing tool calls during evaluation."""

from typing import List

from n2s.core.llm import LlmRequest, LlmResponse
from n2s.core.middleware import LlmMiddleware
from n2s.core.tool import ToolCall


class ToolCallCaptureMiddleware(LlmMiddleware):
    """Capture all tool calls emitted by the LLM during an agent run.

    This is useful for evaluation: it lets us inspect the exact SQL generated
    by the agent without instrumenting every tool implementation.
    """

    def __init__(self) -> None:
        self.captured_tool_calls: List[ToolCall] = []

    async def before_llm_request(self, request: LlmRequest) -> LlmRequest:
        return request

    async def after_llm_response(
        self, request: LlmRequest, response: LlmResponse
    ) -> LlmResponse:
        if response.tool_calls:
            self.captured_tool_calls.extend(response.tool_calls)
        return response
