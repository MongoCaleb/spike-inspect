"""Seeded variant of mcp_setup_first.

Same Sample, but a setup solver runs first to create a realistic dev
environment (empty ~/.zshrc and ~/.bashrc) so the agent has concrete
files to update when the prompt implies "you're on a Mac with zsh".
Tests whether agent behavior moves toward the target trajectory once
the prompt's environmental assumptions are satisfied.
"""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import Generate, Solver, TaskState, chain, solver
from inspect_ai.util import sandbox
from inspect_swe import claude_code

from _evals_lib import load_sample_by_index

EVALS_PATH = Path(
    "/Users/dachary.carey/workspace/agent-skills/testing/mongodb-mcp-setup/evals/evals.json"
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
        dataset=[load_sample_by_index(EVALS_PATH, 0)],
        solver=chain(seed_dev_environment(), claude_code()),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
