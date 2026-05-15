"""Final validation: realistic seed + mongodb-mcp-setup skill loaded.

If skill ON moves the score above 0 while skill OFF (mcp_setup_first_settings)
holds at 0, we have empirical proof of the lift signal that's the demo's
headline finding: the skill's prescriptive instructions push the agent from
"diagnose and defer" to "diagnose and execute".
"""

from __future__ import annotations

import json

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import Generate, Solver, TaskState, chain, solver
from inspect_ai.util import sandbox
from inspect_swe import claude_code

from _evals_lib import evals_path, load_sample_by_index, skill_path

EVALS_PATH = evals_path("mongodb-mcp-setup")
SKILL_PATH = skill_path("mongodb-mcp-setup")

SETTINGS_LOCAL_JSON = json.dumps(
    {
        "mcpServers": {
            "mongodb": {
                "command": "npx",
                "args": ["-y", "mongodb-mcp-server"],
                "env": {
                    "MDB_MCP_CONNECTION_STRING": "${MDB_MCP_CONNECTION_STRING}"
                },
            }
        }
    },
    indent=2,
)


@solver
def seed_claude_settings_local() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        sb = sandbox()
        await sb.write_file(".claude/settings.local.json", SETTINGS_LOCAL_JSON)
        await sb.exec(["bash", "-c", "mkdir -p $HOME/.claude && mv .claude/settings.local.json $HOME/.claude/settings.local.json && touch $HOME/.zshrc && touch $HOME/.bashrc"])
        return state
    return solve


@task
def mcp_setup_first_with_skill() -> Task:
    return Task(
        dataset=[load_sample_by_index(EVALS_PATH, 0)],
        solver=chain(
            seed_claude_settings_local(),
            claude_code(skills=[SKILL_PATH]),
        ),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
