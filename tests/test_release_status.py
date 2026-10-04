"""Shared release receipts use real files and HTTP reads, without voice providers."""

import json
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import release_status as releases
from app.server import create_app

SHA = "a" * 40


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for key in list(releases.os.environ):
        if key.startswith(
            ("VOICEBOT_", "RESTAURANT_", "AZURE_", "GROQ_", "EASY_", "STAY_")
        ):
            monkeypatch.delenv(key)
    monkeypatch.delenv("CALLS_DB", raising=False)


def receipt(tmp_path):
    path = tmp_path / "telephone-release.json"
    releases.record(SHA, releases.identity(), path=path)
    return path, json.loads(path.read_text())


def test_missing_receipt_never_claims_telephone_deployment(tmp_path):
    status = releases.status(path=tmp_path / "missing")
    assert status["status"] == "unverified"
    assert status["telephone_revision"] is None
    assert status["verified_at"] is None


def test_verified_receipt_is_atomic_and_can_be_refreshed_without_artifacts(tmp_path):
    path, payload = receipt(tmp_path)
    assert releases.status(path=path)["status"] == "in_sync"
    assert releases.status(path=path)["telephone_revision"] == SHA
    releases.record("b" * 40, releases.identity(), path=path)
    assert releases.status(path=path)["telephone_revision"] == "b" * 40
    assert list(tmp_path.iterdir()) == [path]
    assert set(payload) == {"revision", "fingerprint", "verified_at"}


def test_stale_receipt_is_not_current_deployment_proof(tmp_path):
    path, payload = receipt(tmp_path)
    boundary = payload["verified_at"] + releases.MAX_AGE
    assert releases.status(path=path, now=boundary)["status"] == "in_sync"
    assert releases.status(path=path, now=boundary + 1)["status"] == "stale"


@pytest.mark.parametrize(
    "key,value",
    [
        ("VOICEBOT_SENTENCE_PAUSE_MS", "240"),
        ("VOICEBOT_TELEPHONE_LANGUAGE", "en"),
        ("VOICEBOT_SPEECH_RATE", "1.0"),
        ("GROQ_CHAT_MODEL", "fixture/new-model"),
        ("AZURE_EN_VOICE", "en-US-GuyNeural"),
        ("RESTAURANT_STATE_DB", "/data/another-booking.db"),
        ("RESTAURANT_DEMO_WRITES", "1"),
    ],
)
def test_changed_shared_settings_invalidate_old_receipt(
    tmp_path, monkeypatch, key, value
):
    path, _ = receipt(tmp_path)
    monkeypatch.setenv(key, value)
    assert releases.status(path=path)["status"] == "out_of_sync"


def test_different_effective_recognizers_cannot_share_or_refresh_receipt(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("AZURE_REGION", "northeurope")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "fixture")
    monkeypatch.setenv("VOICEBOT_STT_PROVIDER", "azure")
    path, _ = receipt(tmp_path)
    azure_identity = releases.identity()
    original = path.read_bytes()
    monkeypatch.setenv("VOICEBOT_STT_PROVIDER", "groq")
    assert releases.status(path=path)["status"] == "out_of_sync"
    with pytest.raises(ValueError, match="release_identity_mismatch"):
        releases.record(SHA, azure_identity, path=path)
    assert path.read_bytes() == original


@pytest.mark.parametrize("provider", ["azure", "groq"])
def test_effective_recognizer_identity_excludes_credential_values(
    monkeypatch, provider
):
    monkeypatch.setenv("AZURE_REGION", "northeurope")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "fixture")
    monkeypatch.setenv("VOICEBOT_STT_PROVIDER", provider)
    before = releases.identity()
    monkeypatch.setenv("AZURE_SPEECH_KEY", "different-fixture")
    monkeypatch.setenv("GROQ_API_KEY", "different-fixture")
    assert releases.identity() == before


def test_automatic_and_explicit_azure_selection_have_same_identity(monkeypatch):
    monkeypatch.setenv("AZURE_REGION", "northeurope")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "fixture")
    default = releases.identity()
    for override in ("", "azure"):
        monkeypatch.setenv("VOICEBOT_STT_PROVIDER", override)
        assert releases.identity() == default


def test_credentials_and_carrier_configuration_never_enter_receipt(
    tmp_path, monkeypatch
):
    before = releases.identity()
    for key in (
        "AZURE_SPEECH_KEY",
        "GROQ_API_KEY",
        "TWILIO_AUTH_TOKEN",
        "LIVEKIT_API_SECRET",
    ):
        monkeypatch.setenv(key, "synthetic-private-never-print")
    assert releases.identity() == before
    path, _ = receipt(tmp_path)
    assert "synthetic-private" not in path.read_text()
    assert "synthetic-private" not in json.dumps(releases.status(path=path))


@pytest.mark.parametrize(
    "revision,fingerprint",
    [
        ("branch-name", "b" * 64),
        (SHA, "invalid"),
        (SHA, "b" * 64),
    ],
)
def test_invalid_or_mismatched_record_keeps_previous_verified_receipt(
    tmp_path, revision, fingerprint
):
    path, _ = receipt(tmp_path)
    original = path.read_bytes()
    with pytest.raises(ValueError):
        releases.record(revision, fingerprint, path=path)
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize(
    "change",
    [
        {"revision": "master"},
        {"revision": None},
        {"fingerprint": "unknown"},
        {"fingerprint": False},
        {"verified_at": True},
        {"verified_at": "today"},
        {"verified_at": float("nan")},
        {"verified_at": float("inf")},
        {"verified_at": 10**400},
        {"verified_at": -1},
        {"verified_at": time.time() + 3600},
        {"unexpected": "synthetic-private"},
    ],
)
def test_malformed_receipt_is_unverified_and_not_echoed(tmp_path, change):
    path, payload = receipt(tmp_path)
    payload.update(change)
    path.write_text(json.dumps(payload))
    assert releases.status(path=path)["status"] == "unverified"
    assert "synthetic-private" not in json.dumps(releases.status(path=path))


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"[1]",
        b"null",
        b"\xff",
        b"x" * 4097,
        b"[" * 1500 + b"0" + b"]" * 1500,
    ],
)
def test_corrupt_or_oversized_receipt_does_not_break_public_status(tmp_path, payload):
    path = tmp_path / "telephone-release.json"
    path.write_bytes(payload)
    assert releases.status(path=path)["status"] == "unverified"


def test_failed_atomic_replace_preserves_old_receipt_and_removes_temporary(tmp_path):
    path, _ = receipt(tmp_path)
    old = path.read_bytes()
    with patch.object(releases.os, "replace", side_effect=OSError):
        with pytest.raises(OSError):
            releases.record(SHA, releases.identity(), path=path)
    assert path.read_bytes() == old
    assert list(tmp_path.iterdir()) == [path]


def test_source_digest_tracks_shared_code_and_data_but_ignores_python_caches(
    tmp_path, monkeypatch
):
    (tmp_path / "app").mkdir()
    (tmp_path / "data/demo").mkdir(parents=True)
    code = tmp_path / "app/example.py"
    code.write_text("example = 1")
    monkeypatch.setattr(releases, "ROOT", tmp_path)
    releases.source_digest.cache_clear()
    try:
        first = releases.source_digest()
        (tmp_path / "app/__pycache__").mkdir()
        (tmp_path / "app/__pycache__/example.pyc").write_bytes(b"cache")
        releases.source_digest.cache_clear()
        assert releases.source_digest() == first
        code.write_text("example = 2")
        releases.source_digest.cache_clear()
        assert releases.source_digest() != first
    finally:
        releases.source_digest.cache_clear()


def test_public_status_exposes_receipt_without_claiming_real_carrier_verification(
    tmp_path,
):
    path, _ = receipt(tmp_path)
    actual = releases.status
    with patch.object(
        releases, "status", side_effect=lambda **kwargs: actual(path=path, **kwargs)
    ):
        with TestClient(create_app()) as client:
            response = client.get("/api/status")
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    telephone = response.json()["telephone"]
    assert telephone["release"]["status"] == "in_sync"
    assert telephone["sentence_pause_ms"] == 0
    assert telephone["carrier_call_verified"] is False
    assert telephone["public_ingress_verified"] is False


def test_same_path_configuration_drift_cannot_refresh_a_loaded_website_receipt(
    tmp_path, monkeypatch
):
    from app.restaurant_data import load_restaurant_data

    config = tmp_path / "restaurant.json"
    original = load_restaurant_data()
    config.write_text(json.dumps(original))
    monkeypatch.setenv("VOICEBOT_BUSINESS_TYPE", "restaurant")
    monkeypatch.setenv("RESTAURANT_CONFIG_PATH", str(config))
    for key, filename in [
        ("CALLS_DB", "calls.db"),
        ("RESTAURANT_STATE_DB", "restaurant.db"),
        ("EASY_STATE_DB", "easy.db"),
        ("STAY_STATE_DB", "stay.db"),
    ]:
        monkeypatch.setenv(key, str(tmp_path / filename))
    path, payload = receipt(tmp_path)
    actual = releases.status
    with patch.object(
        releases, "status", side_effect=lambda **kwargs: actual(path=path, **kwargs)
    ):
        with TestClient(create_app()) as client:
            loaded = client.get("/api/status").json()["telephone"]["release"][
                "web_fingerprint"
            ]
            changed = dict(original, reservation_duration_minutes=120)
            config.write_text(json.dumps(changed))
            assert releases.identity() != loaded
            assert (
                client.get("/api/status").json()["telephone"]["release"][
                    "web_fingerprint"
                ]
                == loaded
            )
            assert (
                client.app.state.stack["restaurant_data"][
                    "reservation_duration_minutes"
                ]
                == 90
            )
            with pytest.raises(ValueError, match="release_identity_mismatch"):
                releases.record(SHA, loaded, path=path)
            assert json.loads(path.read_text()) == payload
            # Even a receipt produced by the old fresh-file CLI path is not
            # alignment proof for the website's still-loaded configuration.
            releases.record(SHA, releases.identity(), path=path)
            assert (
                client.get("/api/status").json()["telephone"]["release"]["status"]
                == "out_of_sync"
            )


def test_cli_invalid_arguments_print_only_a_fixed_code(capsys):
    assert releases.main(["synthetic-private"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == "FAIL: release_receipt_failed"
