"""Run the natural language querying evals through claude_code().

Loads samples from agent-skills/testing/mongodb-natural-language-querying/evals/evals.json
and routes them through Claude Code in a Docker sandbox. Scored by LLM judge
against the expected_output description (which is prose, not a pattern).
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

from _evals_lib import evals_path, load_sample_by_name

EVALS_PATH = evals_path("mongodb-natural-language-querying")


@task
def simple_find() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "simple-find")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def geo_based_find() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "geo-based-find")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_with_nested_match() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-with-nested-match")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_translates_to_agg_mode_count() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-translates-to-agg-mode-count")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_translates_to_agg_total_sum() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-translates-to-agg-total-sum")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_translates_to_agg_max_host() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-translates-to-agg-max-host")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def relative_date_find_last_year() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "relative-date-find-last-year")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def relative_date_find_30_years_ago() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "relative-date-find-30-years-ago")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def number_field_find() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "number-field-find")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_with_complex_projection() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-with-complex-projection")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_with_and_operator() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-with-and-operator")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_with_non_english() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-with-non-english")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_with_regex_string_ops() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-with-regex-string-ops")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_simple_projection() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-simple-projection")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def basic_aggregate() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "basic-aggregate")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_filter_and_projection() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-filter-and-projection")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def geo_based_agg() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "geo-based-agg")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_nested_fields_match() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-nested-fields-match")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_group_sort_limit_project() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-group-sort-limit-project")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_group_sort_limit_project_2() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-group-sort-limit-project-2")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def relative_date_agg_30_years() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "relative-date-agg-30-years")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def relative_date_agg_last_year() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "relative-date-agg-last-year")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_array_slice() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-array-slice")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_multiple_conditions_match() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-multiple-conditions-match")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_non_english() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-non-english")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_simple_sort_limit() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-simple-sort-limit")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_unwind_group() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-unwind-group")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_size_operator() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-size-operator")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_complex_word_frequency() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-complex-word-frequency")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_super_complex_percentage() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-super-complex-percentage")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_complex_regex_string_ops() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-complex-regex-string-ops")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_join_lookup() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-join-lookup")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def agg_simple_projection() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "agg-simple-projection")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def no_redundant_exists_with_comparison() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "no-redundant-exists-with-comparison")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def max_time_ms_option_used() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "max-time-ms-option-used")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )


@task
def find_in_java() -> Task:
    return Task(
        dataset=[load_sample_by_name(EVALS_PATH, "find-in-java")],
        solver=claude_code(),
        scorer=model_graded_qa(),
        sandbox="docker",
    )

