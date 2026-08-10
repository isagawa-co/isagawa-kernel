"""Attestation orchestrator — main entry point for the sigstore attestation pipeline.

Chains: collect hashes -> create bundle -> sign -> log to Rekor -> save locally.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Resolve imports relative to this file's location
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from collect import collect_pipeline_hashes
from intent import read_intent_chain
from schema import create_bundle, validate_bundle
from sign import sign_bundle
from rekor import log_to_rekor, update_bundle_with_rekor


def _extract_backlog_number(backlog_path: str) -> str:
    """Extract the numeric backlog ID from a path like docs/backlog/046-kernel-....md"""
    basename = os.path.basename(backlog_path)
    parts = basename.split("-", 1)
    if parts and parts[0].isdigit():
        return parts[0]
    return "000"


def _resolve_output_paths(task_folder: str) -> list:
    """Discover output artifacts by scanning the task folder's parent project structure."""
    results = []
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(task_folder)))
    gate_contract = os.path.join(task_folder, "gate-contract.md")
    if os.path.isfile(gate_contract):
        results.append(gate_contract)
    if os.path.isdir(task_folder):
        for fname in sorted(os.listdir(task_folder)):
            fpath = os.path.join(task_folder, fname)
            if os.path.isfile(fpath):
                results.append(fpath)
    return results


def _read_workflow_state(task_folder: str) -> dict:
    """Read workflow state to get task counts."""
    workspace = os.path.abspath(task_folder)
    while workspace and not os.path.isfile(os.path.join(workspace, "CLAUDE.md")):
        parent = os.path.dirname(workspace)
        if parent == workspace:
            break
        workspace = parent

    for name in os.listdir(os.path.join(workspace, ".claude", "state")):
        if name.endswith("_workflow.json"):
            with open(os.path.join(workspace, ".claude", "state", name), "r") as f:
                return json.load(f)
    return {}


def run_attestation(
    backlog_path: str,
    task_folder: str,
    output_paths: list = None,
    dry_run: bool = False,
) -> str:
    """Run the full attestation pipeline.

    Args:
        backlog_path: Path to the backlog spec that triggered this pipeline.
        task_folder: Path to the task folder with decomposed tasks.
        output_paths: Explicit list of output artifact paths. If None, auto-discovered.
        dry_run: If True, collect hashes and create bundle but skip signing and Rekor.

    Returns:
        Path to the final attestation bundle JSON file.
    """
    start_time = datetime.now(timezone.utc).isoformat()

    # 1. Resolve output paths if not provided
    if output_paths is None:
        output_paths = _resolve_output_paths(task_folder)

    # 2. Collect hashes
    hashes = collect_pipeline_hashes(backlog_path, task_folder, output_paths)

    # 2b. Read intent chain for this backlog
    backlog_num = _extract_backlog_number(backlog_path)
    raw_chain = read_intent_chain(backlog_num)
    intent_chain = raw_chain if raw_chain else None

    # 3. Read workflow state for task counts
    workflow = _read_workflow_state(task_folder)
    task_count = workflow.get("total_tasks", 0)
    completed_tasks = workflow.get("completed_tasks", [])
    skipped_tasks = workflow.get("skipped_tasks", [])

    # Filter completed_tasks to only those belonging to this task folder
    folder_basename = os.path.basename(task_folder.rstrip("/\\"))
    # completed_tasks is a flat list across all projects; count all for now
    completed_count = len(completed_tasks)
    skipped_count = len(skipped_tasks)

    end_time = datetime.now(timezone.utc).isoformat()

    # 4. Create the attestation bundle
    bundle = create_bundle(
        config_source_hash=hashes["config_source_hash"],
        parameters_hash=hashes["parameters_hash"],
        artifacts=hashes["artifacts"],
        start_time=start_time,
        end_time=end_time,
        pipeline_backlog=backlog_path,
        task_folder=task_folder,
        task_count=task_count,
        completed_count=completed_count,
        skipped_count=skipped_count,
        intent_chain=intent_chain,
    )

    # 5. Validate bundle before saving
    errors = validate_bundle(bundle)
    if errors:
        print(f"WARNING: bundle validation errors: {errors}", file=sys.stderr)

    # 6. Save bundle locally
    backlog_num = _extract_backlog_number(backlog_path)
    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_filename = f"{backlog_num}-{timestamp_slug}.json"

    # Find workspace root
    workspace = os.path.abspath(task_folder)
    while workspace and not os.path.isfile(os.path.join(workspace, "CLAUDE.md")):
        parent = os.path.dirname(workspace)
        if parent == workspace:
            workspace = os.path.abspath(".")
            break
        workspace = parent

    attestations_dir = os.path.join(workspace, ".claude", "state", "attestations")
    os.makedirs(attestations_dir, exist_ok=True)

    bundle_path = os.path.join(attestations_dir, bundle_filename)
    with open(bundle_path, "w") as f:
        json.dump(bundle, f, indent=2)
    print(f"Bundle saved: {bundle_path}")

    if dry_run:
        print("DRY-RUN: skipping signing and Rekor submission")
        return bundle_path

    # 7. Sign the bundle
    sign_result = sign_bundle(bundle_path)
    if sign_result.startswith("ERROR:"):
        print(f"WARNING: signing failed — saving unsigned bundle: {sign_result}", file=sys.stderr)
        return bundle_path

    signed_path = sign_result
    print(f"Signed: {signed_path}")

    # 8. Extract Rekor entry from sigstore bundle (Rekor submission happened during signing)
    rekor_resp = log_to_rekor(signed_path)
    if "error" in rekor_resp:
        print(f"WARNING: Rekor entry extraction failed — bundle still valid: {rekor_resp['error']}", file=sys.stderr)
        return bundle_path

    print(f"Rekor entry: {rekor_resp.get('entryUrl', 'unknown')}")

    # 9. Update local bundle with Rekor entry
    update_result = update_bundle_with_rekor(bundle_path, rekor_resp)
    if update_result != "OK":
        print(f"WARNING: failed to update bundle with Rekor entry: {update_result}", file=sys.stderr)

    return bundle_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run sigstore attestation pipeline")
    parser.add_argument("backlog_path", nargs="?", help="Path to backlog spec")
    parser.add_argument("task_folder", nargs="?", help="Path to task folder")
    parser.add_argument("--dry-run", action="store_true", help="Skip signing and Rekor")
    args = parser.parse_args()

    if not args.backlog_path or not args.task_folder:
        # Self-test mode when no args provided with --dry-run
        if args.dry_run and not args.backlog_path:
            print("Self-test: running dry-run with test data...")
            test_dir = os.path.join(_THIS_DIR, "_test_attest")
            os.makedirs(test_dir, exist_ok=True)

            test_backlog = os.path.join(test_dir, "046-test-backlog.md")
            with open(test_backlog, "w") as f:
                f.write("# Test backlog\nThis is a test.")

            test_task_dir = os.path.join(test_dir, "tasks")
            os.makedirs(test_task_dir, exist_ok=True)
            test_task = os.path.join(test_task_dir, "001-test.md")
            with open(test_task, "w") as f:
                f.write("# Test task\n- [ ] Do something")

            try:
                result = run_attestation(
                    backlog_path=test_backlog,
                    task_folder=test_task_dir,
                    output_paths=[test_backlog],
                    dry_run=True,
                )
                if os.path.isfile(result):
                    with open(result, "r") as f:
                        bundle = json.load(f)
                    print(f"OK: bundle created at {result}")
                    print(f"OK: predicateType = {bundle.get('predicateType')}")
                    print(f"OK: artifacts count = {len(bundle.get('predicate', {}).get('output', {}).get('artifacts', []))}")
                    # Clean up the generated attestation
                    os.remove(result)
                else:
                    print(f"FAIL: expected file at {result}", file=sys.stderr)
                    sys.exit(1)
            finally:
                import shutil
                shutil.rmtree(test_dir, ignore_errors=True)

            print("ALL TESTS PASSED")
            sys.exit(0)
        else:
            parser.print_help()
            sys.exit(1)

    result_path = run_attestation(
        backlog_path=args.backlog_path,
        task_folder=args.task_folder,
        dry_run=args.dry_run,
    )
    print(f"Attestation complete: {result_path}")
    sys.exit(0)
