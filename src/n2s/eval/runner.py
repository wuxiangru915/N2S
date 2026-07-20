"""N2S evaluation runner."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from n2s.core.evaluation import (
    EvaluationDataset,
    TestCase,
    AgentResult,
    TestCaseResult,
    EvaluationResult,
    TrajectoryEvaluator,
    OutputEvaluator,
)
from n2s.core.evaluation.dataset import EvaluationDataset as DatasetLoader
from n2s.core.user import RequestContext
from n2s.demo.agent import create_demo_agent
from n2s.eval.evaluators import SqlExecutionEvaluator, SqlSimilarityEvaluator
from n2s.eval.middleware import ToolCallCaptureMiddleware


@dataclass
class ProviderReport:
    """Report for a single provider run."""

    provider: str
    results: List[TestCaseResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.overall_passed())

    def total_count(self) -> int:
        return len(self.results)

    def accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.overall_score() for r in self.results) / len(self.results)


class N2SEvaluationRunner:
    """Run N2S benchmark across one or more LLM providers."""

    def __init__(
        self,
        database_path: str,
        evaluators: Optional[List[Any]] = None,
    ):
        self.database_path = database_path
        self.evaluators = evaluators or self._default_evaluators(database_path)

    def _default_evaluators(self, database_path: str) -> List[Any]:
        return [
            TrajectoryEvaluator(),
            OutputEvaluator(),
            SqlSimilarityEvaluator(),
            SqlExecutionEvaluator(database_path=database_path),
        ]

    async def run_provider(
        self,
        dataset: EvaluationDataset,
        provider: str,
    ) -> ProviderReport:
        """Run the dataset against a single provider."""
        report = ProviderReport(provider=provider)
        for test_case in dataset.test_cases:
            result = await self._run_test_case(test_case, provider)
            report.results.append(result)
        report.end_time = datetime.now()
        return report

    async def _run_test_case(
        self,
        test_case: TestCase,
        provider: str,
    ) -> TestCaseResult:
        """Execute a single test case and evaluate it."""
        capture = ToolCallCaptureMiddleware()
        agent = create_demo_agent(
            db_path=self.database_path,
            llm_provider=provider,
        )
        agent.llm_middlewares = list(getattr(agent, "llm_middlewares", [])) + [capture]

        request_context = RequestContext(
            cookies={},
            headers={},
            metadata={"test_case_id": test_case.id},
        )

        components = []
        error: Optional[str] = None
        start = asyncio.get_event_loop().time()
        try:
            async for component in agent.send_message(
                request_context=request_context,
                message=test_case.message,
                conversation_id=f"eval-{test_case.id}",
            ):
                components.append(component)
        except Exception as exc:
            error = str(exc)
        elapsed_ms = (asyncio.get_event_loop().time() - start) * 1000

        tool_call_dicts = [
            {
                "tool_name": call.name,
                "arguments": call.arguments,
                "id": call.id,
            }
            for call in capture.captured_tool_calls
        ]

        agent_result = AgentResult(
            test_case_id=test_case.id,
            components=components,
            tool_calls=tool_call_dicts,
            execution_time_ms=elapsed_ms,
            error=error,
        )

        evaluation_results: List[EvaluationResult] = []
        for evaluator in self.evaluators:
            evaluation_results.append(await evaluator.evaluate(test_case, agent_result))

        return TestCaseResult(
            test_case=test_case,
            agent_result=agent_result,
            evaluations=evaluation_results,
            execution_time_ms=elapsed_ms,
        )

    async def run_comparison(
        self,
        dataset: EvaluationDataset,
        providers: List[str],
    ) -> Dict[str, ProviderReport]:
        """Run the dataset against multiple providers in parallel."""
        tasks = [self.run_provider(dataset, provider) for provider in providers]
        reports = await asyncio.gather(*tasks)
        return {report.provider: report for report in reports}


def print_report(report: ProviderReport) -> None:
    """Print a human-readable provider report to stdout."""
    print(f"\nProvider: {report.provider}")
    print("=" * 60)
    for result in report.results:
        status = "PASS" if result.overall_passed() else "FAIL"
        print(
            f"  [{status}] {result.test_case.id}: {result.test_case.message[:60]}... "
            f"({result.execution_time_ms:.0f}ms)"
        )
        for ev in result.evaluations:
            sub = "PASS" if ev.passed else "FAIL"
            print(f"      [{sub}] {ev.evaluator_name}: {ev.reasoning}")
    print("-" * 60)
    print(
        f"Summary: {report.passed_count()}/{report.total_count()} passed, "
        f"accuracy {report.accuracy():.2f}"
    )
