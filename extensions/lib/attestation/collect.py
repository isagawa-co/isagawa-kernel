"""Hash collector for attestation pipeline inputs and outputs."""

import hashlib
import json
import os
import sys


def hash_file(path: str) -> str:
    """Return SHA-256 hex digest of a single file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_directory(dir_path: str) -> list:
    """Walk directory and return [{path, sha256}] for each file."""
    results = []
    for root, _dirs, files in os.walk(dir_path):
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, dir_path)
            results.append({"path": rel, "sha256": hash_file(fpath)})
    results.sort(key=lambda x: x["path"])
    return results


def hash_string(content: str) -> str:
    """Return SHA-256 hex digest of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def collect_pipeline_hashes(
    backlog_path: str, task_folder: str, output_paths: list
) -> dict:
    """Collect all hashes for a pipeline run, ready for create_bundle().

    Returns dict with keys: config_source_hash, parameters_hash, artifacts.
    """
    config_source_hash = hash_file(backlog_path) if os.path.isfile(backlog_path) else ""

    if os.path.isdir(task_folder):
        task_hashes = hash_directory(task_folder)
        parameters_hash = hash_string(json.dumps(task_hashes, sort_keys=True))
    else:
        parameters_hash = ""

    artifacts = []
    for p in output_paths:
        if os.path.isfile(p):
            artifacts.append({"path": p, "sha256": hash_file(p)})
        elif os.path.isdir(p):
            artifacts.extend(
                {"path": os.path.join(p, entry["path"]), "sha256": entry["sha256"]}
                for entry in hash_directory(p)
            )

    return {
        "config_source_hash": config_source_hash,
        "parameters_hash": parameters_hash,
        "artifacts": artifacts,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        own_path = os.path.abspath(__file__)
        digest = hash_file(own_path)
        print(f"{digest}  {own_path}")
        sys.exit(0)
    else:
        print("Usage: python collect.py --test")
        sys.exit(1)
