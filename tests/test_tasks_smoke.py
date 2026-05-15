"""Smoke tests for the per-skill task modules in tasks/.

For each (module, skill_folder) pair, verifies:
- The module imports cleanly.
- Its EVALS_PATH points to a real evals.json on disk.
- The number of @task-decorated functions equals the number of evals.
- Each @task function instantiates a Task whose dataset has exactly one
  Sample whose metadata id/skill match an eval in evals.json.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"

# tasks modules import `from _evals_lib import ...`, so tasks/ must be on path.
sys.path.insert(0, str(TASKS_DIR))


MODULES = [
    ("atlas_stream_processing", "atlas-stream-processing"),
    ("mongodb_connection", "mongodb-connection"),
    ("mcp_setup", "mongodb-mcp-setup"),
    ("natural_language_querying", "mongodb-natural-language-querying"),
    ("query_optimizer", "mongodb-query-optimizer"),
    ("schema_design", "mongodb-schema-design"),
    ("search_and_ai", "mongodb-search-and-ai"),
]


def _load_module(name: str):
    path = TASKS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"tasks.{name}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _task_funcs(mod) -> list:
    """Return @task-decorated functions in source order."""
    src = Path(mod.__file__).read_text()
    tree = ast.parse(src)
    names = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and any(
            isinstance(d, ast.Name) and d.id == "task" for d in node.decorator_list
        )
    ]
    return [getattr(mod, n) for n in names]


@pytest.mark.parametrize("module_name,skill_folder", MODULES)
def test_module_imports(module_name: str, skill_folder: str):
    mod = _load_module(module_name)
    assert hasattr(mod, "EVALS_PATH")
    assert Path(mod.EVALS_PATH).is_file(), f"EVALS_PATH missing: {mod.EVALS_PATH}"


@pytest.mark.parametrize("module_name,skill_folder", MODULES)
def test_task_count_matches_evals(module_name: str, skill_folder: str):
    mod = _load_module(module_name)
    evals = json.loads(Path(mod.EVALS_PATH).read_text())["evals"]
    funcs = _task_funcs(mod)
    assert len(funcs) == len(evals), (
        f"{module_name}: {len(funcs)} @task funcs vs {len(evals)} evals"
    )


@pytest.mark.parametrize("module_name,skill_folder", MODULES)
def test_each_task_loads_one_known_sample(module_name: str, skill_folder: str):
    mod = _load_module(module_name)
    data = json.loads(Path(mod.EVALS_PATH).read_text())
    known_ids = {e["id"] for e in data["evals"]}
    skill_name = data["skill_name"]

    seen_ids: set[int] = set()
    for fn in _task_funcs(mod):
        task_obj = fn()
        samples = list(task_obj.dataset)
        assert len(samples) == 1, f"{module_name}.{fn.__name__}: expected 1 sample"
        sample = samples[0]
        assert sample.input, f"{module_name}.{fn.__name__}: empty input"
        assert sample.metadata is not None
        assert sample.metadata["skill"] == skill_name
        assert sample.metadata["id"] in known_ids, (
            f"{module_name}.{fn.__name__}: id {sample.metadata['id']} not in evals.json"
        )
        seen_ids.add(sample.metadata["id"])

    assert seen_ids == known_ids, (
        f"{module_name}: covered ids {sorted(seen_ids)} != evals.json ids {sorted(known_ids)}"
    )
