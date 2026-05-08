"""Seeded variant of mcp_setup_first.

Same Sample, but a setup solver runs first to create a realistic dev
environment (empty ~/.zshrc and ~/.bashrc) so the agent has concrete
files to update when the prompt implies "you're on a Mac with zsh".
Tests whether agent behavior moves toward the target trajectory once
the prompt's environmental assumptions are satisfied.
"""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import Generate, Solver, TaskState, chain, solver
from inspect_ai.util import sandbox
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


@solver
def seed_dev_environment() -> Solver:
    """Create empty shell profiles so the agent has files to update."""
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        await sandbox().exec(
            ["bash", "-c", "touch $HOME/.zshrc && touch $HOME/.bashrc"]
        )
        return state
    return solve


@task
def mcp_setup_first_seeded() -> Task:
    return Task(
        dataset=[load_first_sample()],
        solver=chain(seed_dev_environment(), claude_code()),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
