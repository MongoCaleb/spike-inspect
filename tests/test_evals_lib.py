"""Unit tests for tasks/_evals_lib.py path resolution helpers.

Covers the three-tier resolution chain (AGENT_SKILLS_DIR env var, sibling
fallback, RuntimeError) and the path-building helpers built on top of it.

Each test isolates env state via monkeypatch.delenv and stubs the resolver's
`__file__` when the sibling-fallback branch is under test, so no real
filesystem state leaks across tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# tasks/_evals_lib.py imports `from inspect_ai.dataset import Sample` at
# module level, so the path-helper tests still pay the inspect_ai import
# cost, but they don't touch its sample-loading code.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tasks"))
import _evals_lib  # noqa: E402
from _evals_lib import agent_skills_root, evals_path, skill_path  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("AGENT_SKILLS_DIR", raising=False)


def _make_sibling_layout(tmp_path: Path) -> tuple[Path, Path]:
    """Create <tmp>/repo/tasks/_evals_lib_stub.py and <tmp>/agent-skills/
    so the sibling fallback (parents[2] / 'agent-skills') resolves."""
    repo = tmp_path / "repo"
    (repo / "tasks").mkdir(parents=True)
    stub = repo / "tasks" / "_evals_lib_stub.py"
    stub.write_text("")
    sibling = tmp_path / "agent-skills"
    sibling.mkdir()
    return stub, sibling


def test_env_var_resolves(tmp_path, monkeypatch):
    target = tmp_path / "my-clone"
    target.mkdir()
    monkeypatch.setenv("AGENT_SKILLS_DIR", str(target))
    assert agent_skills_root() == target


def test_env_var_expands_user(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    target = tmp_path / "skills"
    target.mkdir()
    monkeypatch.setenv("AGENT_SKILLS_DIR", "~/skills")
    assert agent_skills_root() == target


def test_env_var_pointing_to_nonexistent_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_SKILLS_DIR", str(tmp_path / "nope"))
    with pytest.raises(RuntimeError, match="AGENT_SKILLS_DIR"):
        agent_skills_root()


def test_env_var_pointing_to_file_raises(tmp_path, monkeypatch):
    f = tmp_path / "not_a_dir"
    f.write_text("")
    monkeypatch.setenv("AGENT_SKILLS_DIR", str(f))
    with pytest.raises(RuntimeError, match="not a directory"):
        agent_skills_root()


def test_sibling_fallback_resolves(tmp_path, monkeypatch):
    stub, sibling = _make_sibling_layout(tmp_path)
    monkeypatch.setattr(_evals_lib, "__file__", str(stub))
    assert agent_skills_root() == sibling


def test_env_var_wins_over_sibling(tmp_path, monkeypatch):
    stub, sibling = _make_sibling_layout(tmp_path)
    monkeypatch.setattr(_evals_lib, "__file__", str(stub))
    override = tmp_path / "override"
    override.mkdir()
    monkeypatch.setenv("AGENT_SKILLS_DIR", str(override))
    assert agent_skills_root() == override


def test_missing_both_raises_with_helpful_message(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "tasks").mkdir(parents=True)
    stub = repo / "tasks" / "_evals_lib_stub.py"
    stub.write_text("")
    monkeypatch.setattr(_evals_lib, "__file__", str(stub))
    expected_sibling = tmp_path / "agent-skills"
    with pytest.raises(RuntimeError, match=str(expected_sibling)) as exc_info:
        agent_skills_root()
    assert "AGENT_SKILLS_DIR" in str(exc_info.value)


def test_evals_path_shape(tmp_path, monkeypatch):
    target = tmp_path / "clone"
    target.mkdir()
    monkeypatch.setenv("AGENT_SKILLS_DIR", str(target))
    assert evals_path("foo") == target / "testing" / "foo" / "evals" / "evals.json"


def test_skill_path_shape(tmp_path, monkeypatch):
    target = tmp_path / "clone"
    target.mkdir()
    monkeypatch.setenv("AGENT_SKILLS_DIR", str(target))
    assert skill_path("foo") == target / "skills" / "foo"
