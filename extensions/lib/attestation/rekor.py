"""Rekor transparency log integration for attestation bundles.

With sigstore-python, Rekor submission happens automatically during signing.
This module extracts Rekor entry info from sigstore bundles and updates
local attestation bundles with the Rekor data.
"""

import json
import os
import sys


def extract_rekor_entry(sigstore_bundle_path: str) -> dict:
    """Extract Rekor entry info from a sigstore bundle.

    sigstore-python includes Rekor data in its output bundle automatically.

    Args:
        sigstore_bundle_path: Path to the .sigstore.json file from sign_bundle().

    Returns:
        Dict with 'entryUrl' and 'logIndex' on success,
        or dict with 'error' key on failure.
    """
    if not os.path.isfile(sigstore_bundle_path):
        return {"error": f"sigstore bundle not found: {sigstore_bundle_path}"}

    try:
        with open(sigstore_bundle_path, "r") as f:
            bundle_data = json.load(f)
    except json.JSONDecodeError as e:
        return {"error": f"invalid JSON: {e}"}

    # sigstore bundle format has verificationMaterial.tlogEntries
    tlog_entries = (
        bundle_data
        .get("verificationMaterial", {})
        .get("tlogEntries", [])
    )

    if not tlog_entries:
        return {"error": "no Rekor tlog entries found in sigstore bundle"}

    entry = tlog_entries[0]
    log_index = entry.get("logIndex")
    log_id = entry.get("logId", {}).get("keyId", "")

    # Construct the entry URL
    entry_url = ""
    if log_index is not None:
        entry_url = f"https://search.sigstore.dev/?logIndex={log_index}"

    return {
        "entryUrl": entry_url,
        "logIndex": log_index,
        "logId": log_id,
    }


def log_to_rekor(signed_bundle_path: str, dry_run: bool = False) -> dict:
    """Get Rekor entry info. With sigstore-python, this extracts from the bundle
    rather than making a separate submission.

    Args:
        signed_bundle_path: Path to the .sigstore.json file.
        dry_run: If True, return simulated response.

    Returns:
        Dict with 'entryUrl' and 'logIndex' on success,
        or dict with 'error' key on failure.
    """
    if dry_run:
        return {
            "entryUrl": "https://search.sigstore.dev/?logIndex=DRY-RUN",
            "logIndex": "DRY-RUN",
            "dryRun": True,
        }

    return extract_rekor_entry(signed_bundle_path)


def verify_rekor_entry(log_index: str, dry_run: bool = False) -> bool:
    """Verify a Rekor entry exists by checking the search URL.

    Args:
        log_index: The Rekor log index to verify.
        dry_run: If True, return True without network call.

    Returns:
        True if entry exists, False otherwise.
    """
    if not log_index:
        return False

    if dry_run:
        return True

    try:
        import requests
        resp = requests.get(
            f"https://rekor.sigstore.dev/api/v1/log/entries?logIndex={log_index}",
            timeout=30,
        )
        return resp.status_code == 200 and len(resp.json()) > 0
    except Exception:
        return False


def update_bundle_with_rekor(bundle_path: str, rekor_response: dict) -> str:
    """Add Rekor entry info to a local attestation bundle JSON file.

    Args:
        bundle_path: Path to the attestation bundle JSON file to update.
        rekor_response: Dict from log_to_rekor() or extract_rekor_entry().

    Returns:
        'OK' on success, or an error string on failure.
    """
    if not os.path.isfile(bundle_path):
        return f"ERROR: bundle not found: {bundle_path}"

    if "error" in rekor_response:
        return f"ERROR: cannot update bundle with failed rekor response: {rekor_response['error']}"

    try:
        with open(bundle_path, "r") as f:
            bundle = json.load(f)
    except json.JSONDecodeError as e:
        return f"ERROR: invalid JSON in bundle: {e}"

    if "predicate" not in bundle:
        bundle["predicate"] = {}

    bundle["predicate"]["rekor"] = {
        "entryUrl": rekor_response.get("entryUrl", ""),
        "logIndex": rekor_response.get("logIndex", ""),
    }

    with open(bundle_path, "w") as f:
        json.dump(bundle, f, indent=2)

    return "OK"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--extract":
        if len(sys.argv) < 3:
            print("Usage: python rekor.py --extract <signed.sigstore.json>")
            sys.exit(1)
        result = extract_rekor_entry(sys.argv[2])
        print(json.dumps(result, indent=2))
        sys.exit(0 if "error" not in result else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        result = log_to_rekor("", dry_run=True)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Self-test: dry-run + update_bundle_with_rekor
        test_bundle = {
            "predicateType": "natural-language-session/v1",
            "predicate": {"invocation": {"configSource": "abc", "parameters": "def"}},
        }
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_rekor_bundle.json")
        with open(test_path, "w") as f:
            json.dump(test_bundle, f)

        rekor_resp = log_to_rekor(test_path, dry_run=True)
        if "error" in rekor_resp:
            print(f"FAIL: log_to_rekor dry-run: {rekor_resp['error']}", file=sys.stderr)
            os.remove(test_path)
            sys.exit(1)
        print(f"OK: log_to_rekor dry-run: entryUrl={rekor_resp['entryUrl']}")

        verified = verify_rekor_entry(rekor_resp["logIndex"], dry_run=True)
        if not verified:
            print("FAIL: verify_rekor_entry dry-run returned False", file=sys.stderr)
            os.remove(test_path)
            sys.exit(1)
        print(f"OK: verify_rekor_entry dry-run: {verified}")

        update_result = update_bundle_with_rekor(test_path, rekor_resp)
        if update_result != "OK":
            print(f"FAIL: update_bundle_with_rekor: {update_result}", file=sys.stderr)
            os.remove(test_path)
            sys.exit(1)

        with open(test_path, "r") as f:
            updated = json.load(f)
        if "rekor" not in updated.get("predicate", {}):
            print("FAIL: rekor key missing from updated bundle", file=sys.stderr)
            os.remove(test_path)
            sys.exit(1)
        print(f"OK: update_bundle_with_rekor: rekor.entryUrl={updated['predicate']['rekor']['entryUrl']}")

        os.remove(test_path)
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("Usage: python rekor.py --extract <signed.sigstore.json>")
        print("       python rekor.py --dry-run")
        print("       python rekor.py --test")
        sys.exit(1)
