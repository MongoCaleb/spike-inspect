"""Run the atlas-stream-processing evals through claude_code().

Loads samples from agent-skills/testing/atlas-stream-processing/evals/evals.json
and routes them through Claude Code in a Docker sandbox. Scored by LLM judge
against the expected_output description (which is prose, not a pattern).
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

from _evals_lib import evals_path, load_sample_by_name

EVALS_PATH = evals_path("atlas-stream-processing")


@task
def create_workspace_basic() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-workspace-basic")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def add_kafka_connection() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "add-kafka-connection")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def list_workspaces() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "list-workspaces")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def inspect_processor_health() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "inspect-processor-health")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def create_simple_kafka_to_mongo() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-simple-kafka-to-mongo")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def create_windowed_aggregation() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-windowed-aggregation")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def debug_failed_processor() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "debug-failed-processor")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def debug_zero_output_windowed() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "debug-zero-output-windowed")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def stop_processor() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "stop-processor")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def modify_processor_pipeline() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "modify-processor-pipeline")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def create_changestream_to_kafka() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-changestream-to-kafka")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def tier_sizing_complex_pipeline() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "tier-sizing-complex-pipeline")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def create_https_enrichment() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-https-enrichment")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def validate_connections_before_deploy() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "validate-connections-before-deploy")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def create_lambda_integration() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-lambda-integration")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def delete_workspace_safely() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "delete-workspace-safely")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def get_operational_logs() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "get-operational-logs")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def region_format_validation() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "region-format-validation")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def billing_warning_before_start() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "billing-warning-before-start")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def create_s3_sink() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-s3-sink")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def search_knowledge_before_processor() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "search-knowledge-before-processor")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def classify_processor_output() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "classify-processor-output")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def handle_402_billing_error() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "handle-402-billing-error")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def multi_connection_setup() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "multi-connection-setup")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def chained_processors() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "chained-processors")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def create_privatelink_kafka_aws() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "create-privatelink-kafka-aws")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

