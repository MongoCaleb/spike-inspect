"""Realistically seeded variant of mcp_setup_first.

Plants the broken state the prompt implies:
  - The mongodb MCP server IS configured (via inspect_swe's mcp_servers param,
    which passes --mcp-config to the Claude Code CLI on launch)
  - The MCP config references ${MDB_MCP_CONNECTION_STRING}
  - The env var is NOT set in the shell
  - ~/.zshrc exists (empty) for the agent to update

The "broken connection" the user reports has a single root cause: the env var
the MCP server needs at launch isn't exported in the shell profile. The agent
should diagnose this and produce the expected_output trajectory.
"""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import Generate, Solver, TaskState, chain, solver
from inspect_ai.tool import MCPServerConfigStdio
from inspect_ai.util import sandbox
from inspect_swe import claude_code

EVALS_PATH = Path(
    "/Users/dachary.carey/workspace/agent-skills/testing/mongodb-mcp-setup/evals/evals.json"
)

MONGODB_MCP_SERVER = MCPServerConfigStdio(
    name="mongodb",
    command="npx",
    args=["-y", "mongodb-mcp-server"],
    env={"MDB_MCP_CONNECTION_STRING": "${MDB_MCP_CONNECTION_STRING}"},
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
def mcp_setup_first_realistic() -> Task:
    return Task(
        dataset=[load_first_sample()],
        solver=chain(
            seed_dev_environment(),
            claude_code(mcp_servers=[MONGODB_MCP_SERVER]),
        ),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
