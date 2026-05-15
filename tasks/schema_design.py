"""Run the schema design eval through claude_code().

Loads the schema design sample from agent-skills/testing/mongodb-schema-design/evals/evals.json
and routes it through Claude Code in a Docker sandbox. Scored by LLM judge
against the expected_output description (which is prose, not a pattern).
"""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

from _evals_lib import load_sample_by_name

EVALS_PATH = Path(
    "/Users/caleb.thompson/Projects/mongodb/agent-skills/testing/mongodb-schema-design/evals/evals.json"
)

@task
def schema_versioning_migration() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "schema-versioning-migration")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def product_view_counter() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "product-view-counter")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def product_reviews_embed_vs_reference() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "product-reviews-embed-vs-reference")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def blog_comments_outlier_pattern() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "blog-comments-outlier-pattern")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def extended_reference_lookup_performance() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "extended-reference-lookup-performance")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def polymorphic_pattern_product_types() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "polymorphic-pattern-product-types")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

