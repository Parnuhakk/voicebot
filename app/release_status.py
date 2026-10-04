"""Private controller receipts; public reads never imply a tested carrier call."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

from .business import business_type, restaurant_database, restaurant_writes_enabled
from .providers.azure_stt import stt_descriptor
from .providers.speech_delivery import SpeechDelivery
from .providers.voice_config import SpeechConfig, VoiceConfig

ROOT = Path(__file__).resolve().parents[1]
REPORT = Path("/data/telephone-release.json")
MAX_AGE = 180
MAX_BYTES = 4096
HEX = re.compile(r"[0-9a-f]{64}")


@lru_cache(maxsize=1)
def source_digest() -> str:
    """Hash immutable files shared by both images, ignoring Python caches."""
    digest = hashlib.sha256()
    for directory in (ROOT / "app", ROOT / "data/demo"):
        for path in sorted(directory.rglob("*")):
            if (
                not path.is_file()
                or "__pycache__" in path.parts
                or path.suffix in {".pyc", ".pyo"}
            ):
                continue
            digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def identity(*, restaurant_data: dict | None = None) -> str:
    """Only common behavior settings; credentials never enter the receipt."""
    env = os.environ
    business = business_type()
    settings = {
        "source": source_digest(),
        "business": business,
        "models": asdict(VoiceConfig.from_env()),
        "recognition": stt_descriptor(),
        "speech": asdict(SpeechConfig.from_env()),
        "delivery": asdict(SpeechDelivery.from_env()),
        "azure_region": env.get("AZURE_REGION", ""),
        "calls_db": env.get("CALLS_DB", "/data/calls.db"),
    }
    if business == "restaurant":
        from .restaurant_data import load_restaurant_data

        settings["restaurant"] = {
            "database": restaurant_database(),
            "writes": restaurant_writes_enabled(),
            "config": env.get("RESTAURANT_CONFIG_PATH", ""),
            "data": restaurant_data
            if restaurant_data is not None
            else load_restaurant_data(),
        }
    else:
        settings["hotel"] = {
            "easy_db": env.get("EASY_STATE_DB", "/data/easy-booking.db"),
            "stay_db": env.get("STAY_STATE_DB") or "/data/stay-booking.db",
            "writes": env.get("EASY_DEMO_WRITES", "0") == "1",
            "stay_writes": env.get("STAY_DEMO_WRITES", env.get("EASY_DEMO_WRITES", "0"))
            == "1",
        }
    return hashlib.sha256(
        json.dumps(settings, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def record(revision: str, web_identity: str, *, path: Path = REPORT) -> None:
    """Called only after the host controller verifies both healthy services."""
    if not re.fullmatch(r"[0-9a-f]{40}", revision) or not HEX.fullmatch(web_identity):
        raise ValueError("release_receipt_invalid")
    telephone_identity = identity()
    if telephone_identity != web_identity:
        raise ValueError("release_identity_mismatch")
    receipt = {
        "revision": revision,
        "fingerprint": telephone_identity,
        "verified_at": time.time(),
    }
    # Atomic replacement prevents a concurrent public read seeing half a report.
    descriptor, temporary = tempfile.mkstemp(
        prefix=".telephone-release-", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(receipt, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def status(
    *,
    path: Path = REPORT,
    now: float | None = None,
    restaurant_data: dict | None = None,
) -> dict[str, str | float | None]:
    current = identity(restaurant_data=restaurant_data)
    result: dict[str, str | float | None] = {
        "status": "unverified",
        "web_fingerprint": current,
        "telephone_fingerprint": None,
        "telephone_revision": None,
        "verified_at": None,
        "max_age_seconds": MAX_AGE,
    }
    try:
        with path.open("rb") as stream:
            payload = stream.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            return result
        receipt = json.loads(payload)
        if not isinstance(receipt, dict) or set(receipt) != {
            "revision",
            "fingerprint",
            "verified_at",
        }:
            return result
        revision, fingerprint, checked = (
            receipt["revision"],
            receipt["fingerprint"],
            receipt["verified_at"],
        )
        if (
            not isinstance(revision, str)
            or not re.fullmatch(r"[0-9a-f]{40}", revision)
            or not isinstance(fingerprint, str)
            or not HEX.fullmatch(fingerprint)
            or isinstance(checked, bool)
            or not isinstance(checked, (int, float))
            or not math.isfinite(checked)
            or checked <= 0
        ):
            return result
        age = (time.time() if now is None else now) - checked
        if age < -5:
            return result
    except (OSError, ValueError, TypeError, OverflowError, RecursionError):
        return result
    result.update(
        telephone_fingerprint=fingerprint,
        telephone_revision=revision,
        verified_at=checked,
        status=(
            "out_of_sync"
            if fingerprint != current
            else "stale"
            if age > MAX_AGE
            else "in_sync"
        ),
    )
    return result


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        if args == ["identity"]:
            print(identity())
        elif len(args) == 3 and args[0] == "record":
            record(args[1], args[2])
        else:
            raise ValueError
        return 0
    except Exception:
        print("FAIL: release_receipt_failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
