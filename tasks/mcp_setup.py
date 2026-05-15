"""Run the mongodb-mcp-setup evals through claude_code().

Loads samples from agent-skills/testing/mongodb-mcp-setup/evals/evals.json
and routes them through Claude Code in a Docker sandbox. Scored by LLM judge
against the expected_output description (which is prose, not a pattern).
"""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

from _evals_lib import load_sample_by_id

EVALS_PATH = Path(
    "/Users/caleb.thompson/Projects/mongodb/agent-skills/testing/mongodb-mcp-setup/evals/evals.json"
)


@task
def eval_1() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 1)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_2() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 2)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_3() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 3)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
