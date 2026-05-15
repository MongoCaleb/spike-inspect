"""Run the mongodb-query-optimizer evals through claude_code().

Loads samples from agent-skills/testing/mongodb-query-optimizer/evals/evals.json
and routes them through Claude Code in a Docker sandbox. Scored by LLM judge
against the expected_output description (which is prose, not a pattern).
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

from _evals_lib import evals_path, load_sample_by_id

EVALS_PATH = evals_path("mongodb-query-optimizer")


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
