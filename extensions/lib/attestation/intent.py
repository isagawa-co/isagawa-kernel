"""Intent chain logger for attestation pipeline.

Records the SHA-256 hash of raw user input and the resulting backlog file
at each revision. Raw text is ONLY hashed — never stored. Privacy by design.
"""

import hashlib
import json
import os
import sys

# Allow running from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect import hash_file, hash_string


INTENTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", ".claude", "state", "intents",
)


def _intent_chain_path(backlog_number: str) -> str:
    """Return the JSONL path for a given backlog number."""
    return os.path.join(INTENTS_DIR, f"{backlog_number}-intent-chain.jsonl")


def record_intent(backlog_number: str, raw_text: str, backlog_path: str) -> dict:
    """Record an intent chain entry.

    Args:
        backlog_number: e.g. "048"
        raw_text: the raw user input (hashed, never stored)
        backlog_path: path to the backlog .md file (hashed after write)

    Returns:
        The entry dict that was appended.
    """
    os.makedirs(INTENTS_DIR, exist_ok=True)

    chain_path = _intent_chain_path(backlog_number)

    # Auto-increment rev
    rev = 1
    if os.path.isfile(chain_path):
        with open(chain_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            rev = len(lines) + 1

    from datetime import datetime, timezone
    entry = {
        "rev": rev,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_input_hash": hash_string(raw_text),
        "backlog_hash_after": hash_file(backlog_path) if os.path.isfile(backlog_path) else "",
    }

    with open(chain_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    return entry


def read_intent_chain(backlog_number: str) -> list:
    """Read the intent chain for a backlog number.

    Returns:
        List of entry dicts, or empty list if no chain exists.
    """
    chain_path = _intent_chain_path(backlog_number)
    if not os.path.isfile(chain_path):
        return []

    entries = []
    with open(chain_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def _self_test():
    """Self-test: record and read back an intent chain entry."""
    import tempfile
    import shutil

    # Save original INTENTS_DIR and override for test
    global INTENTS_DIR
    original_dir = INTENTS_DIR
    test_dir = tempfile.mkdtemp(prefix="intent-test-")
    INTENTS_DIR = test_dir

    try:
        # Create a fake backlog file
        backlog_file = os.path.join(test_dir, "test-backlog.md")
        with open(backlog_file, "w", encoding="utf-8") as f:
            f.write("# Test Backlog\nSome content.\n")

        # Record
        entry = record_intent("999", "test raw input", backlog_file)
        assert entry["rev"] == 1, f"Expected rev=1, got {entry['rev']}"
        assert entry["raw_input_hash"] == hash_string("test raw input")
        assert entry["backlog_hash_after"] == hash_file(backlog_file)
        assert "timestamp" in entry

        # Record again — rev should increment
        entry2 = record_intent("999", "second input", backlog_file)
        assert entry2["rev"] == 2, f"Expected rev=2, got {entry2['rev']}"

        # Read
        chain = read_intent_chain("999")
        assert len(chain) == 2, f"Expected 2 entries, got {len(chain)}"
        assert chain[0]["rev"] == 1
        assert chain[1]["rev"] == 2

        # Read non-existent
        empty = read_intent_chain("000")
        assert empty == [], f"Expected empty list, got {empty}"

        print("OK: all intent self-tests passed")
        return 0
    finally:
        INTENTS_DIR = original_dir
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python intent.py record NNN \"raw text\" path/to/backlog.md")
        print("  python intent.py read NNN")
        print("  python intent.py --test")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "--test":
        sys.exit(_self_test())
    elif cmd == "record":
        if len(sys.argv) != 5:
            print("Usage: python intent.py record NNN \"raw text\" path/to/backlog.md")
            sys.exit(1)
        entry = record_intent(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(entry, indent=2))
    elif cmd == "read":
        if len(sys.argv) != 3:
            print("Usage: python intent.py read NNN")
            sys.exit(1)
        chain = read_intent_chain(sys.argv[2])
        print(json.dumps(chain, indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
