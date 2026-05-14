"""Unit tests for compare.py.

Covers:
- _result_from_log on a real success EvalLog (metrics extracted, error=None).
- _result_from_log on a real error EvalLog (error.message surfaced, no metrics).
- _result_from_log task_ref derivation when the spec is file-level (no @func).
- _result_from_log fallback to spec.task when the log has no task_file.
- run_one file-level expansion: one RunResult per EvalLog returned by inspect_eval.
- run_one exception path: a single error RunResult with the raised string.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from inspect_ai.log import read_eval_log

# Import target module from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compare  # noqa: E402
from compare import (  # noqa: E402
    RunSpec, _fmt_err, _result_from_log, expand_specs, run_one,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SUCCESS_LOG = FIXTURES / "hello_basic_success.eval"
ERROR_LOG = FIXTURES / "hello_anthropic_error.eval"


@pytest.fixture
def success_log():
    return read_eval_log(str(SUCCESS_LOG))


@pytest.fixture
def error_log():
    return read_eval_log(str(ERROR_LOG))


def test_result_from_log_success(success_log):
    spec = RunSpec(task="tasks/hello.py@hello_basic", model="anthropic/claude-sonnet-4-5")
    r = _result_from_log(spec, "http://127.0.0.1:7676/anthropic", success_log)

    assert r.task == "tasks/hello.py@hello_basic"
    assert r.model == "anthropic/claude-sonnet-4-5"
    assert r.status == "success"
    assert r.error is None
    assert r.samples == 1
    assert r.metric_name == "accuracy"
    assert r.score == 1.0
    assert r.log_file == success_log.location
    # Both accuracy + stderr present, in the order produced by the scorer.
    by_name = {m["name"]: m for m in r.metrics}
    assert set(by_name) == {"accuracy", "stderr"}
    assert by_name["accuracy"]["scorer"] == "includes"
    assert by_name["accuracy"]["value"] == 1.0
    assert by_name["stderr"]["value"] == 0.0


def test_result_from_log_error_surfaces_message(error_log):
    spec = RunSpec(task="tasks/hello.py", model="openai/gpt-4o")
    r = _result_from_log(spec, "http://127.0.0.1:7676/openai", error_log)

    assert r.status == "error"
    assert r.score is None
    assert r.metric_name is None
    assert r.metrics == []
    assert r.samples is None
    assert r.error is not None
    # Real message starts with the RuntimeError from the proxy bridge.
    assert "Model proxy process exited unexpectedly" in r.error


def test_result_from_log_derives_task_ref_for_file_level_spec(success_log):
    # Caller passed a file-level spec; result should expand to the @func ref
    # from the log itself.
    spec = RunSpec(task="tasks/hello.py", model="anthropic/claude-sonnet-4-5")
    r = _result_from_log(spec, "http://x", success_log)
    assert r.task == "tasks/hello.py@hello_basic"


def test_result_from_log_falls_back_to_spec_task_when_no_task_file():
    spec = RunSpec(task="tasks/whatever.py@thing", model="openai/gpt-4o")
    fake = SimpleNamespace(
        eval=SimpleNamespace(task_file=None, task=None),
        results=None, status="success", location="x.eval", error=None,
    )
    r = _result_from_log(spec, "http://x", fake)
    assert r.task == "tasks/whatever.py@thing"


def test_run_one_file_level_expansion_fans_out(monkeypatch, success_log, error_log):
    """A file-level RunSpec produces one RunResult per EvalLog returned by
    inspect_eval, each with its own task_ref derived from the log."""
    captured: dict = {}

    def fake_eval(**kwargs):
        captured.update(kwargs)
        return [success_log, error_log]

    monkeypatch.setattr(compare, "inspect_eval", fake_eval)
    spec = RunSpec(task="tasks/hello.py", model="anthropic/claude-sonnet-4-5")
    results = run_one(spec, "http://127.0.0.1:7676", "./logs")

    # inspect_eval received the file-level task and a derived /anthropic base_url.
    assert captured["tasks"] == "tasks/hello.py"
    assert captured["model"] == "anthropic/claude-sonnet-4-5"
    assert captured["model_base_url"] == "http://127.0.0.1:7676/anthropic"
    assert "display" not in captured  # sequential path doesn't force display

    assert len(results) == 2
    assert results[0].task == "tasks/hello.py@hello_basic"
    assert results[0].status == "success"
    assert results[1].task == "tasks/hello.py@hello_anthropic"
    assert results[1].status == "error"
    assert results[1].error and "Model proxy" in results[1].error


def test_run_one_passes_display_when_provided(monkeypatch, success_log):
    captured: dict = {}

    def fake_eval(**kwargs):
        captured.update(kwargs)
        return [success_log]

    monkeypatch.setattr(compare, "inspect_eval", fake_eval)
    spec = RunSpec(task="tasks/hello.py@hello_basic", model="openai/gpt-4o")
    run_one(spec, "http://127.0.0.1:7676", "./logs", display="log")
    assert captured["display"] == "log"


def test_run_one_exception_returns_single_error_result(monkeypatch):
    def boom(**_kwargs):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(compare, "inspect_eval", boom)
    spec = RunSpec(task="tasks/hello.py@hello_basic", model="openai/gpt-4o")
    results = run_one(spec, "http://127.0.0.1:7676", "./logs")

    assert len(results) == 1
    r = results[0]
    assert r.status == "error"
    assert r.task == "tasks/hello.py@hello_basic"
    assert r.score is None
    assert r.metrics == []
    assert r.error == "kaboom"


def test_expand_specs_fans_out_file_level_spec():
    """A file-level spec (no @func) is fanned out to one spec per @task in
    the file so a per-task materialization failure (e.g. load_sample_by_name
    raising) only fails that task, not the whole file."""
    spec = RunSpec(task="tasks/hello.py", model="anthropic/claude-sonnet-4-5")
    expanded = expand_specs([spec])

    # tasks/hello.py defines multiple @task funcs; we should get one spec per.
    assert len(expanded) >= 2
    assert all("@" in s.task for s in expanded)
    assert all(s.task.startswith("tasks/hello.py@") for s in expanded)
    assert all(s.model == "anthropic/claude-sonnet-4-5" for s in expanded)
    assert all(s.base_url is None for s in expanded)


def test_expand_specs_passes_through_task_level_specs():
    spec = RunSpec(task="tasks/hello.py@hello_basic",
                   model="openai/gpt-4o", base_url="http://x")
    expanded = expand_specs([spec])
    assert len(expanded) == 1
    assert expanded[0].task == "tasks/hello.py@hello_basic"
    assert expanded[0].model == "openai/gpt-4o"
    assert expanded[0].base_url == "http://x"


def test_fmt_err_trims_missing_sample_message_to_name_only():
    """The 'No sample found with name ...' error carries a long absolute
    path that's noise in the printed table; we want just the name part."""
    msg = ("No sample found with name 'unnecessary-collections-sharding-by-date' "
           "in /Users/x/agent-skills/testing/mongodb-schema-design/evals/evals.json")
    assert _fmt_err(msg) == (
        "No sample found with name 'unnecessary-collections-sharding-by-date'"
    )


def test_fmt_err_passes_through_unrelated_errors():
    assert _fmt_err("kaboom") == "kaboom"
    assert _fmt_err(None) == "-"


def test_expand_specs_passes_through_missing_file():
    """Unparseable / nonexistent files pass through so inspect_eval can
    surface the underlying error rather than being silently dropped."""
    spec = RunSpec(task="tasks/does_not_exist.py", model="openai/gpt-4o")
    expanded = expand_specs([spec])
    assert len(expanded) == 1
    assert expanded[0].task == "tasks/does_not_exist.py"
