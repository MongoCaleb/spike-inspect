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

@task
def unnecessary_collections_sharding_by_date() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "unnecessary-collections-sharding-by-date")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def unnecessary_indexes_bloat() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "unnecessary-indexes-bloat")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def sql_migration_normalized_schema() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "sql-migration-normalized-schema")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def unbounded_array_document_size() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "unbounded-array-document-size")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def schema_validation_new_collection() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "schema-validation-new-collection")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def iot_time_series_data() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "iot-time-series-data")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def computed_pattern_dashboard_aggregation() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "computed-pattern-dashboard-aggregation")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

@task
def archive_pattern_data_lifecycle() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "archive-pattern-data-lifecycle")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
