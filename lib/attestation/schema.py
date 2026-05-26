"""Attestation schema for natural-language-session/v1 bundles."""

import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Optional


PREDICATE_TYPE = "natural-language-session/v1"

REQUIRED_FIELDS = [
    "predicateType",
    "predicate.invocation.configSource",
    "predicate.invocation.parameters",
    "predicate.output.artifacts",
    "predicate.timestamp.start",
    "predicate.timestamp.end",
    "predicate.metadata.pipeline_backlog",
    "predicate.metadata.task_folder",
    "predicate.metadata.task_count",
    "predicate.metadata.completed_count",
    "predicate.metadata.skipped_count",
]


@dataclass
class Artifact:
    path: str
    sha256: str


@dataclass
class Invocation:
    configSource: str
    parameters: str


@dataclass
class Timestamp:
    start: str
    end: str


@dataclass
class Metadata:
    pipeline_backlog: str
    task_folder: str
    task_count: int
    completed_count: int
    skipped_count: int


@dataclass
class Predicate:
    invocation: Invocation
    output: dict = field(default_factory=lambda: {"artifacts": []})
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(start="", end=""))
    metadata: Metadata = field(default_factory=lambda: Metadata(
        pipeline_backlog="", task_folder="", task_count=0,
        completed_count=0, skipped_count=0
    ))


@dataclass
class AttestationBundle:
    predicateType: str = PREDICATE_TYPE
    predicate: Predicate = field(default_factory=lambda: Predicate(
        invocation=Invocation(configSource="", parameters="")
    ))


def create_bundle(
    config_source_hash: str,
    parameters_hash: str,
    artifacts: List[dict],
    start_time: str,
    end_time: str,
    pipeline_backlog: str,
    task_folder: str,
    task_count: int,
    completed_count: int,
    skipped_count: int,
    intent_chain: Optional[List[dict]] = None,
) -> dict:
    """Create an attestation bundle dict from inputs."""
    invocation = {
        "configSource": config_source_hash,
        "parameters": parameters_hash,
    }
    if intent_chain is not None:
        invocation["intent_chain"] = intent_chain

    return {
        "predicateType": PREDICATE_TYPE,
        "predicate": {
            "invocation": invocation,
            "output": {
                "artifacts": [
                    {"path": a["path"], "sha256": a["sha256"]}
                    for a in artifacts
                ],
            },
            "timestamp": {
                "start": start_time,
                "end": end_time,
            },
            "metadata": {
                "pipeline_backlog": pipeline_backlog,
                "task_folder": task_folder,
                "task_count": task_count,
                "completed_count": completed_count,
                "skipped_count": skipped_count,
            },
        },
    }


def _get_nested(d: dict, dotted_key: str):
    """Traverse a dict by dotted key path. Returns None if any key is missing."""
    keys = dotted_key.split(".")
    current = d
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return None
        current = current[k]
    return current


def validate_bundle(bundle: dict) -> List[str]:
    """Validate an attestation bundle. Returns list of error strings (empty = valid)."""
    errors = []

    for field_path in REQUIRED_FIELDS:
        value = _get_nested(bundle, field_path)
        if value is None:
            errors.append(f"missing required field: {field_path}")
        elif isinstance(value, str) and not value:
            errors.append(f"empty required field: {field_path}")

    predicate_type = bundle.get("predicateType")
    if predicate_type and predicate_type != PREDICATE_TYPE:
        errors.append(
            f"invalid predicateType: expected '{PREDICATE_TYPE}', got '{predicate_type}'"
        )

    artifacts = _get_nested(bundle, "predicate.output.artifacts")
    if isinstance(artifacts, list):
        for i, art in enumerate(artifacts):
            if not isinstance(art, dict):
                errors.append(f"artifact[{i}] is not a dict")
                continue
            if "path" not in art:
                errors.append(f"artifact[{i}] missing 'path'")
            if "sha256" not in art:
                errors.append(f"artifact[{i}] missing 'sha256'")

    return errors


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        raw = sys.stdin.read()
        try:
            bundle = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"FAIL: invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        errors = validate_bundle(bundle)
        if errors:
            print("FAIL: validation errors:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)
        else:
            print("OK: bundle is valid")
            sys.exit(0)
    else:
        print("Usage: python schema.py --validate < bundle.json")
        sys.exit(1)
