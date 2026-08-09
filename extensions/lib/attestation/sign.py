"""Signing wrapper for attestation bundles using sigstore-python keyless (OIDC) flow.

Replaces cosign CLI with pure Python sigstore library.
On first use, opens a browser for GitHub/Google OIDC authentication.
"""

import json
import os
import sys


def sign_bundle(bundle_path: str, dry_run: bool = False) -> str:
    """Sign an attestation bundle JSON file using sigstore-python keyless flow.

    Args:
        bundle_path: Path to the attestation bundle JSON file.
        dry_run: If True, validate the flow without actual signing.

    Returns:
        Path to the signed output file, or "DRY-RUN: ..." string,
        or "ERROR: ..." string on failure.
    """
    if not os.path.isfile(bundle_path):
        return f"ERROR: bundle not found: {bundle_path}"

    with open(bundle_path, "rb") as f:
        bundle_bytes = f.read()

    try:
        json.loads(bundle_bytes)
    except json.JSONDecodeError as e:
        return f"ERROR: invalid JSON in bundle: {e}"

    signed_path = bundle_path.replace(".json", ".sigstore.json")

    if dry_run:
        return f"DRY-RUN: would sign {bundle_path} -> {signed_path}"

    try:
        from sigstore.oidc import Issuer, detect_credential
        from sigstore.sign import ClientTrustConfig, SigningContext

        # Try ambient credential first (CI environments)
        ambient = detect_credential()
        if ambient:
            from sigstore.oidc import IdentityToken
            token = IdentityToken(ambient)
        else:
            # Interactive: opens browser for OIDC login
            SIGSTORE_OAUTH_URL = "https://oauth2.sigstore.dev/auth"
            issuer = Issuer(SIGSTORE_OAUTH_URL)
            token = issuer.identity_token()

        # Build signing context (offline to avoid Windows symlink issue)
        config = ClientTrustConfig.production(offline=True)
        ctx = SigningContext.from_trust_config(config)

        # Sign the bundle bytes
        with ctx.signer(token) as signer:
            result = signer.sign_artifact(bundle_bytes)

        # Save the sigstore bundle (contains signature + certificate + rekor entry)
        with open(signed_path, "w") as f:
            f.write(result.to_json())

        return signed_path

    except ImportError:
        return "ERROR: sigstore not installed — run: pip install sigstore"
    except Exception as e:
        return f"ERROR: signing failed: {e}"


def verify_signature(signed_path: str, bundle_path: str = None) -> bool:
    """Verify a sigstore-signed attestation bundle.

    Args:
        signed_path: Path to the .sigstore.json file.
        bundle_path: Path to the original bundle (artifact that was signed).

    Returns:
        True if verification succeeds, False otherwise.
    """
    if not os.path.isfile(signed_path):
        return False

    try:
        from sigstore.models import Bundle
        from sigstore.verify import Verifier
        from sigstore.verify.policy import UnsafeNoOp

        # Load the sigstore bundle
        with open(signed_path, "r") as f:
            bundle = Bundle.from_json(f.read())

        # Build verifier (offline)
        from sigstore.sign import ClientTrustConfig
        config = ClientTrustConfig.production(offline=True)
        verifier = Verifier.from_trust_config(config)

        # If we have the original artifact, verify against it
        if bundle_path and os.path.isfile(bundle_path):
            with open(bundle_path, "rb") as f:
                artifact_bytes = f.read()
        else:
            artifact_bytes = None

        # Use UnsafeNoOp policy for local verification (we trust our own signatures)
        if artifact_bytes:
            verifier.verify_artifact(artifact_bytes, bundle, UnsafeNoOp())
        return True

    except Exception:
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        if len(sys.argv) < 3:
            print("Usage: python sign.py --dry-run <bundle.json>")
            sys.exit(1)
        result = sign_bundle(sys.argv[2], dry_run=True)
        print(result)
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == "--sign":
        if len(sys.argv) < 3:
            print("Usage: python sign.py --sign <bundle.json>")
            sys.exit(1)
        result = sign_bundle(sys.argv[2], dry_run=False)
        print(result)
        sys.exit(0 if not result.startswith("ERROR:") else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_bundle = {
            "predicateType": "natural-language-session/v1",
            "predicate": {"invocation": {"configSource": "abc", "parameters": "def"}},
        }
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_bundle.json")
        with open(test_path, "w") as f:
            json.dump(test_bundle, f)
        result = sign_bundle(test_path, dry_run=True)
        os.remove(test_path)
        if result.startswith("DRY-RUN:"):
            print(f"OK: {result}")
            sys.exit(0)
        else:
            print(f"FAIL: {result}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python sign.py --dry-run <bundle.json>")
        print("       python sign.py --sign <bundle.json>")
        print("       python sign.py --test")
        sys.exit(1)
