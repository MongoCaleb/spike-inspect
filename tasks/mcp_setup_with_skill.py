"""Final validation: realistic seed + mongodb-mcp-setup skill loaded.

If skill ON moves the score above 0 while skill OFF (mcp_setup_first_settings)
holds at 0, we have empirical proof of the lift signal that's the demo's
headline finding: the skill's prescriptive instructions push the agent from
"diagnose and defer" to "diagnose and execute".
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
SKILL_PATH = Path(
    "/Users/dachary.carey/workspace/agent-skills/skills/mongodb-mcp-setup"
)

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


def load_first_sample() -> Sample:
    data = json.loads(EVALS_PATH.read_text())
    first = data["evals"][0]
    return Sample(
        input=first["prompt"],
        target=first["expected_output"],
        metadata={"id": first["id"], "skill": data["skill_name"]},
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
        dataset=[load_first_sample()],
        solver=chain(
            seed_claude_settings_local(),
            claude_code(skills=[SKILL_PATH]),
        ),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
