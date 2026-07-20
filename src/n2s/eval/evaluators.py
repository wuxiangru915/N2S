"""N2S-specific SQL evaluators for Text2SQL benchmark."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

import pandas as pd
import sqlparse

from n2s.core.evaluation import Evaluator, TestCase, AgentResult, EvaluationResult


def _extract_run_sql_calls(agent_result: AgentResult) -> List[str]:
    """Return SQL strings from captured run_sql tool calls."""
    sqls: List[str] = []
    for call in agent_result.tool_calls:
        tool_name = call.get("name") or call.get("tool_name")
        if tool_name != "run_sql":
            continue
        arguments = call.get("arguments") or {}
        sql = arguments.get("sql")
        if sql:
            sqls.append(sql)
    return sqls


def _normalize_sql(sql: str) -> str:
    """Normalize SQL for string comparison."""
    try:
        formatted = sqlparse.format(
            sql, strip_comments=True, keyword_case="lower", strip_whitespace=True
        )
    except Exception:
        formatted = sql
    return " ".join(formatted.lower().split())


class SqlExecutionEvaluator(Evaluator):
    """Execute the generated SQL and compare the result to the expected answer."""

    def __init__(self, database_path: str):
        self.database_path = database_path

    @property
    def name(self) -> str:
        return "sql_execution"

    async def evaluate(
        self, test_case: TestCase, agent_result: AgentResult
    ) -> EvaluationResult:
        expected = test_case.expected_outcome
        if not expected:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=True,
                score=1.0,
                reasoning="No expected outcome specified, passing by default",
            )

        if agent_result.error:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=False,
                score=0.0,
                reasoning=f"Agent execution failed: {agent_result.error}",
            )

        sqls = _extract_run_sql_calls(agent_result)
        if not sqls:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=False,
                score=0.0,
                reasoning="No run_sql tool call was captured",
            )

        generated_sql = sqls[0]
        expected_result = expected.metadata.get("expected_result")

        try:
            conn = sqlite3.connect(self.database_path)
            df = pd.read_sql_query(generated_sql, conn)
            conn.close()
        except Exception as e:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=False,
                score=0.0,
                reasoning=f"Generated SQL failed to execute: {e}",
                metrics={"generated_sql": generated_sql},
            )

        if expected_result is not None:
            # Scalar comparison if result is a single cell, otherwise compare CSV.
            if df.shape == (1, 1):
                actual = str(df.iloc[0, 0])
            else:
                actual = df.to_csv(index=False).strip()
            passed = str(expected_result).strip() == actual.strip()
            score = 1.0 if passed else 0.0
            reasoning = (
                f"Expected result '{expected_result}', got '{actual}'"
                if not passed
                else f"Result matched expected value '{expected_result}'"
            )
        else:
            passed = True
            score = 1.0
            reasoning = "SQL executed successfully and no expected_result was specified"

        return EvaluationResult(
            test_case_id=test_case.id,
            evaluator_name=self.name,
            passed=passed,
            score=score,
            reasoning=reasoning,
            metrics={
                "generated_sql": generated_sql,
                "expected_result": expected_result,
                "row_count": len(df),
                "columns": df.columns.tolist(),
            },
        )


class SqlSimilarityEvaluator(Evaluator):
    """Compare generated SQL to a reference SQL using normalized string equality."""

    @property
    def name(self) -> str:
        return "sql_similarity"

    async def evaluate(
        self, test_case: TestCase, agent_result: AgentResult
    ) -> EvaluationResult:
        expected = test_case.expected_outcome
        if not expected:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=True,
                score=1.0,
                reasoning="No expected outcome specified, passing by default",
            )

        if agent_result.error:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=False,
                score=0.0,
                reasoning=f"Agent execution failed: {agent_result.error}",
            )

        expected_sql = expected.metadata.get("expected_sql")
        if not expected_sql:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=True,
                score=1.0,
                reasoning="No expected_sql specified, passing by default",
            )

        sqls = _extract_run_sql_calls(agent_result)
        if not sqls:
            return EvaluationResult(
                test_case_id=test_case.id,
                evaluator_name=self.name,
                passed=False,
                score=0.0,
                reasoning="No run_sql tool call was captured",
            )

        generated_sql = sqls[0]
        passed = _normalize_sql(generated_sql) == _normalize_sql(expected_sql)
        score = 1.0 if passed else 0.0
        reasoning = (
            "Generated SQL matches expected SQL after normalization"
            if passed
            else f"Generated SQL differs from expected SQL"
        )

        return EvaluationResult(
            test_case_id=test_case.id,
            evaluator_name=self.name,
            passed=passed,
            score=score,
            reasoning=reasoning,
            metrics={
                "generated_sql": generated_sql,
                "expected_sql": expected_sql,
            },
        )
