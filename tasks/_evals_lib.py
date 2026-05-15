"""Shared loaders for skill evals.json files."""

from __future__ import annotations

import json
import os
from pathlib import Path

from inspect_ai.dataset import Sample


def agent_skills_root() -> Path:
    """Resolve the mongodb/agent-skills clone root.

    Order: $AGENT_SKILLS_DIR, then a sibling 'agent-skills' next to this repo,
    otherwise raise with both options spelled out so the failure is fixable
    without reading source."""
    env = os.environ.get("AGENT_SKILLS_DIR")
    if env:
        p = Path(env).expanduser()
        if not p.is_dir():
            raise RuntimeError(f"AGENT_SKILLS_DIR={env!r} is not a directory")
        return p
    sibling = Path(__file__).resolve().parents[2] / "agent-skills"
    if sibling.is_dir():
        return sibling
    raise RuntimeError(
        "agent-skills checkout not found. Set AGENT_SKILLS_DIR to the path of "
        "your mongodb/agent-skills clone, or clone it as a sibling of this "
        f"repo at {sibling}."
    )


def evals_path(testing_subdir: str) -> Path:
    """Path to a testing/<subdir>/evals/evals.json file in agent-skills."""
    return agent_skills_root() / "testing" / testing_subdir / "evals" / "evals.json"


def skill_path(name: str) -> Path:
    """Path to a skills/<name> directory in agent-skills."""
    return agent_skills_root() / "skills" / name


def load_sample_by_index(evals_path: Path, index: int) -> Sample:
    data = json.loads(evals_path.read_text())
    sample = data["evals"][index]
    return Sample(
        input=sample["prompt"],
        target=sample.get("expected_output") or "",
        metadata={"id": sample["id"], "skill": data["skill_name"]},
    )


def load_sample_by_name(evals_path: Path, name: str) -> Sample:
    data = json.loads(evals_path.read_text())
    for sample in data["evals"]:
        if sample["name"] == name:
            return Sample(
                input=sample["prompt"],
                target=sample.get("expected_output") or "",
                metadata={"id": sample["id"], "skill": data["skill_name"]},
            )
    raise ValueError(f"No sample found with name {name!r} in {evals_path}")


def load_sample_by_id(evals_path: Path, id: int) -> Sample:
    data = json.loads(evals_path.read_text())
    for sample in data["evals"]:
        if sample["id"] == id:
            return Sample(
                input=sample["prompt"],
                target=sample.get("expected_output") or "",
                metadata={"id": sample["id"], "skill": data["skill_name"]},
            )
    raise ValueError(f"No sample found with id {id!r} in {evals_path}")
