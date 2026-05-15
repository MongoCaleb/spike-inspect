"""Shared loaders for skill evals.json files."""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai.dataset import Sample


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
