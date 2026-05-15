"""Unit tests for compare.py.

Covers:
- _result_from_log on a real success EvalLog (metrics extracted, error=None).
- _result_from_log on a real error EvalLog (error.message surfaced, no metrics).
- _result_from_log task_ref derivation when the spec is file-level (no @func).
- _result_from_log fallback to spec.task when the log has no task_file.
- run_one file-level expansion: one RunResult per EvalLog returned by inspect_eval.
- run_one exception path: a single error RunResult with the raised string.
- build_matrix_specs cross-product shape.
- _all_task_files enumerates tasks/*.py and skips underscore-prefixed files.
- main() argparse validation for --all-files / --models / --config combos.
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
    RunSpec, _all_task_files, _fmt_err, _result_from_log,
    build_matrix_specs, expand_specs, run_one, validate_model_name,
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
    spec = RunSpec(task="tests/hello.py", model="anthropic/claude-sonnet-4-5")
    expanded = expand_specs([spec])

    # tests/hello.py defines multiple @task funcs; we should get one spec per.
    assert len(expanded) >= 2
    assert all("@" in s.task for s in expanded)
    assert all(s.task.startswith("tests/hello.py@") for s in expanded)
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


def test_build_matrix_specs_is_cross_product():
    tasks = ["tasks/a.py", "tasks/b.py"]
    models = ["anthropic/x", "openai/y", "anthropic/z"]
    specs = build_matrix_specs(tasks, models)
    assert len(specs) == 6
    # Outer loop is tasks, inner is models.
    assert (specs[0].task, specs[0].model) == ("tasks/a.py", "anthropic/x")
    assert (specs[2].task, specs[2].model) == ("tasks/a.py", "anthropic/z")
    assert (specs[3].task, specs[3].model) == ("tasks/b.py", "anthropic/x")
    assert all(s.base_url is None for s in specs)


def test_build_matrix_specs_empty_inputs():
    assert build_matrix_specs([], ["openai/x"]) == []
    assert build_matrix_specs(["tasks/a.py"], []) == []


def test_all_task_files_returns_real_files_and_skips_underscore(tmp_path, monkeypatch):
    """_all_task_files lists tasks/*.py and skips _*-prefixed files
    (which are private helpers like _evals_lib.py, not @task modules)."""
    fake_tasks = tmp_path / "tasks"
    fake_tasks.mkdir()
    (fake_tasks / "alpha.py").write_text("")
    (fake_tasks / "beta.py").write_text("")
    (fake_tasks / "_helpers.py").write_text("")
    (fake_tasks / "notes.txt").write_text("")  # non-.py also ignored by glob

    monkeypatch.setattr(compare, "TASKS_DIR", fake_tasks)
    refs = _all_task_files()
    assert refs == ["tasks/alpha.py", "tasks/beta.py"]


def test_all_task_files_against_real_repo():
    """Smoke check against the real tasks/ dir: every ref is tasks/<name>.py,
    none start with _, and well-known files are present."""
    refs = _all_task_files()
    assert refs, "expected at least one tasks/*.py file"
    assert all(r.startswith("tasks/") and r.endswith(".py") for r in refs)
    assert all(not r.removeprefix("tasks/").startswith("_") for r in refs)
    assert "tasks/mongodb_connection.py" in refs


def _run_main(monkeypatch, argv: list[str]) -> int:
    """Invoke compare.main() with a fake argv. Returns the exit code; argparse
    errors raise SystemExit which the caller should expect."""
    monkeypatch.setattr(sys, "argv", ["compare.py", *argv])
    return compare.main()


def test_main_errors_on_all_files_without_models(monkeypatch, capsys):
    with pytest.raises(SystemExit) as exc:
        _run_main(monkeypatch, ["--dry-run", "--all-files"])
    assert exc.value.code == 2
    assert "--all-files requires --models" in capsys.readouterr().err


def test_main_falls_through_to_interactive_when_only_models_given(monkeypatch, capsys):
    """--models alone (no --run, no --all-files) has nothing to fan out across,
    so main() falls through to interactive(). Stub it so the test doesn't
    block on stdin; an empty interactive return surfaces 'No runs specified.'
    on stderr and main() returns 1."""
    called = {"n": 0}

    def fake_interactive():
        called["n"] += 1
        return [], "http://127.0.0.1:7676"

    monkeypatch.setattr(compare, "interactive", fake_interactive)
    rc = _run_main(monkeypatch, ["--dry-run", "--models", "openai/gpt-4o"])
    assert rc == 1
    assert called["n"] == 1
    assert "No runs specified." in capsys.readouterr().err


def test_main_errors_on_all_files_with_config(monkeypatch, capsys, tmp_path):
    cfg = tmp_path / "compare.json"
    cfg.write_text('{"runs": []}')
    with pytest.raises(SystemExit) as exc:
        _run_main(monkeypatch, [
            "--dry-run", "--all-files", "--models", "openai/gpt-4o",
            "--config", str(cfg),
        ])
    assert exc.value.code == 2
    assert "--all-files / --models cannot be combined with --config" in capsys.readouterr().err


def test_main_all_files_plus_models_dry_run_fans_out(monkeypatch, capsys):
    """End-to-end argparse path: --all-files + --models fans out to one
    (task_ref, model) pair per (@task, model) and prints them under --dry-run
    without calling inspect_eval. Pinning _all_task_files to a single real
    file (tests/hello.py) keeps the assertion stable across repo growth."""
    monkeypatch.setattr(compare, "_all_task_files", lambda: ["tests/hello.py"])

    rc = _run_main(monkeypatch, [
        "--dry-run", "--all-files",
        "--models", "anthropic/claude-sonnet-4-5,openai/gpt-4o",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    # tests/hello.py has 3 @tasks (hello_basic / hello_anthropic / hello_openai)
    # crossed with 2 models == 6 rows.
    assert "runs (6):" in out
    assert "tests/hello.py@hello_basic  model=anthropic/claude-sonnet-4-5" in out
    assert "tests/hello.py@hello_openai  model=openai/gpt-4o" in out
    # base_url derivation per provider:
    assert "base_url=http://127.0.0.1:7676/anthropic" in out
    assert "base_url=http://127.0.0.1:7676/openai" in out


@pytest.mark.parametrize("model", [
    "anthropic/claude-sonnet-4-5",
    "openai/gpt-4o",
    "azureai/openai/gpt-4o",  # nested slashes still have non-empty provider/name
])
def test_validate_model_name_accepts_valid(model):
    assert validate_model_name(model) is None


@pytest.mark.parametrize("model", [
    "gpt-5.3-codex",  # the case in the user's bug report
    "",
    "/gpt-4o",        # empty provider
    "openai/",        # empty model
    "no-slash-here",
])
def test_validate_model_name_rejects_invalid(model):
    err = validate_model_name(model)
    assert err is not None
    # Match inspect_ai's own wording so users see one consistent message.
    assert err == (
        f"Model name {model!r} should be in the format of "
        f"<api_name>/<model_name>."
    )


def test_main_stops_run_when_model_name_is_malformed(monkeypatch, capsys):
    """Validation rejects before inspect_eval is reached -- mirrors the user's
    failure on 'gpt-5.3-codex'. main() returns 2 and the error lands on
    stderr; --dry-run output is suppressed."""
    monkeypatch.setattr(compare, "inspect_eval",
                        lambda **_k: pytest.fail("inspect_eval should not be called"))
    rc = _run_main(monkeypatch, [
        "--dry-run",
        "--run", "tests/hello.py@hello_basic:gpt-5.3-codex",
    ])
    assert rc == 2
    out = capsys.readouterr()
    assert "Model name 'gpt-5.3-codex' should be in the format of" in out.err
    assert "runs (" not in out.out


def test_main_dedupes_malformed_model_across_matrix(monkeypatch, capsys):
    """A bad model fanned out across many @tasks should print the error once,
    not once per row."""
    monkeypatch.setattr(compare, "_all_task_files", lambda: ["tests/hello.py"])
    rc = _run_main(monkeypatch, [
        "--dry-run", "--all-files",
        "--models", "anthropic/claude-sonnet-4-5,gpt-5.3-codex",
    ])
    assert rc == 2
    err = capsys.readouterr().err
    # Exactly one occurrence of the bad-model error line.
    assert err.count("'gpt-5.3-codex'") == 1


def test_main_run_plus_all_files_is_additive(monkeypatch, capsys):
    """--run specs come first, then the --all-files matrix is appended."""
    monkeypatch.setattr(compare, "_all_task_files", lambda: ["tests/hello.py"])

    rc = _run_main(monkeypatch, [
        "--dry-run",
        "--run", "tests/hello.py@hello_basic:openai/gpt-4o",
        "--all-files", "--models", "anthropic/claude-sonnet-4-5",
    ])
    assert rc == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("  task=")]
    # 1 explicit --run + 3 @tasks from hello.py * 1 model == 4 rows.
    assert len(lines) == 4
    # The explicit --run lands first; the matrix follows.
    assert "tests/hello.py@hello_basic" in lines[0]
    assert "model=openai/gpt-4o" in lines[0]
    assert all("model=anthropic/claude-sonnet-4-5" in ln for ln in lines[1:])
