"""Run the first mongodb-mcp-setup eval through claude_code().

Loads the first sample from agent-skills/testing/mongodb-mcp-setup/evals.json
and routes it through Claude Code in a Docker sandbox. Scored by LLM judge
against the expected_output description (which is prose, not a pattern).
"""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

from _evals_lib import load_sample_by_index

EVALS_PATH = Path(
    "/Users/dachary.carey/workspace/agent-skills/testing/mongodb-mcp-setup/evals/evals.json"
)


@task
def mcp_setup_first() -> Task:
    return Task(
        dataset=[load_sample_by_index(EVALS_PATH, 0)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
