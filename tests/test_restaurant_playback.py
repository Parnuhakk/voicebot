"""Deterministic receipt lifecycle; native decoding is checked in Playwright."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "case",
    ["buffering", "partial", "seek", "pause", "terminal_race", "eof_race",
     "stale", "expired", "changed_text"],
)
def test_restaurant_playback_receipt_boundaries(case: str) -> None:
    result = subprocess.run(
        ["node", str(ROOT / "tests/restaurant_playback_checks.cjs"), case],
        cwd=ROOT, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == case + "_ok"
