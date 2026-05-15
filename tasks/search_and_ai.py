"""Run the mongodb-search-and-ai evals through claude_code().

Loads samples from agent-skills/testing/mongodb-search-and-ai/evals/evals.json
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
    "/Users/caleb.thompson/Projects/mongodb/agent-skills/testing/mongodb-search-and-ai/evals/evals.json"
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


@task
def eval_4() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 4)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_5() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 5)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_6() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 6)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_7() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 7)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_8() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 8)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_9() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 9)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_10() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 10)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_11() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 11)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_12() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 12)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_13() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 13)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_14() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 14)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def eval_15() -> Task:
    return Task(
        dataset=[load_sample_by_id(EVALS_PATH, 15)],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
