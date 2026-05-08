"""Run the first mongodb-mcp-setup eval through claude_code().

Loads the first sample from agent-skills/testing/mongodb-mcp-setup/evals.json
and routes it through Claude Code in a Docker sandbox. Scored by LLM judge
against the expected_output description (which is prose, not a pattern).
"""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

EVALS_PATH = Path(
    "/Users/dachary.carey/workspace/agent-skills/testing/mongodb-mcp-setup/evals/evals.json"
)


def load_first_sample() -> Sample:
    data = json.loads(EVALS_PATH.read_text())
    first = data["evals"][0]
    return Sample(
        input=first["prompt"],
        target=first["expected_output"],
        metadata={"id": first["id"], "skill": data["skill_name"]},
    )


@task
def mcp_setup_first() -> Task:
    return Task(
        dataset=[load_first_sample()],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
