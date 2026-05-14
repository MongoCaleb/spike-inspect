"""Seed via ~/.claude/settings.local.json (which inspect_swe does NOT overwrite).

The previous attempts surfaced an introspection mismatch: the agent investigates
config files, not runtime state. Passing mcp_servers via claude_code() loads
the server in-session but doesn't appear in any file. inspect_swe overwrites
~/.claude/settings.json with apiKeyHelper, but it leaves settings.local.json
alone - and Claude Code reads settings.local.json (the agent's own report
confirmed it checks for it). This seed plants the config there.
"""

from __future__ import annotations

import json
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
    """Plant the broken state in a file Claude Code reads but inspect_swe doesn't touch."""
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        sb = sandbox()
        # The settings.local.json file Claude Code uses for user-level overrides.
        # inspect_swe overwrites settings.json (with apiKeyHelper) but doesn't touch this one.
        await sb.write_file(".claude/settings.local.json", SETTINGS_LOCAL_JSON)
        # Move it to $HOME (write_file is relative to sandbox cwd; we want HOME)
        await sb.exec(["bash", "-c", "mkdir -p $HOME/.claude && mv .claude/settings.local.json $HOME/.claude/settings.local.json && touch $HOME/.zshrc && touch $HOME/.bashrc"])
        return state
    return solve


@task
def mcp_setup_first_settings() -> Task:
    return Task(
        dataset=[load_sample_by_index(EVALS_PATH, 0)],
        solver=chain(seed_claude_settings_local(), claude_code()),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
