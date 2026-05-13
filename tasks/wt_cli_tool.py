"""Run the wt-cli-tool evals through claude_code().

Loads samples from agent-skills/testing/storage-engines/wt-cli-tool/evals/evals.json
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
    "/Users/caleb.thompson/Projects/mongodb/agent-skills/testing/storage-engines/wt-cli-tool/evals/evals.json"
)

@task
def list_tables() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 1)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def dump_collection() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 2)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def history_store_stats() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 3)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def print_journal_log() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 4)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def verify_tables() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 5)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def salvage_corrupted_database() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 6)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
