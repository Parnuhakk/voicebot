"""Keep the independently authored trilingual research material reproducible."""

import copy
import csv
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "docs/research/restaurant-customer-questions"
spec = importlib.util.spec_from_file_location("restaurant_research_builder", HERE / "build_catalog.py")
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def test_catalog_is_reproducible_and_all_languages_have_complete_answers():
    catalog = builder.build()
    assert catalog == builder.build()
    assert catalog == json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    assert catalog["counts"]["concepts"] == 270
    assert catalog["counts"]["language_pairs"] == 810
    assert len(catalog["counts"]["categories"]) == 17
    assert sum(catalog["counts"]["statuses"].values()) == len(catalog["entries"])
    for entry in catalog["entries"]:
        assert set(entry["question"]) == set(entry["answer"]) == {"et", "en", "ru"}
        assert all(entry["question"].values()) and all(entry["answer"].values())
        assert entry["delivery"] == "research_proposal"


def test_csv_has_all_pairs_and_unknown_owner_fields_remain_null():
    with (HERE / "questions.csv").open(encoding="utf-8-sig", newline="") as stream:
        records = list(csv.DictReader(stream))
    assert len(records) == 810
    assert len({(row["id"], row["language"]) for row in records}) == 810
    owner = json.loads((HERE / "owner-fields.json").read_text(encoding="utf-8"))
    assert set(owner["confirmed_family_facilities"].values()) == {True}
    assert len(owner["fields"]) == 216
    assert len({row["field"] for row in owner["fields"]}) == 216
    assert all(row["value"] is None and row["confirmed_by"] is None for row in owner["fields"])


@pytest.mark.parametrize("content", ["missing|columns", "a|b|c|d|e|f|g|", "a|b|c|d|e|f|g|h|extra"])
def test_invalid_source_row_is_rejected(tmp_path, content):
    path = tmp_path / "invalid.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="nonempty columns"):
        list(builder.rows(path, 8))


def test_html_escapes_embedded_data_and_generation_is_deterministic(tmp_path, monkeypatch):
    catalog = copy.deepcopy(builder.build())
    catalog["entries"][0]["question"]["et"] = "</script><script>throw new Error('unsafe')</script>"
    (tmp_path / "review-template.html").write_text((HERE / "review-template.html").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "sources.json").write_text((HERE / "sources.json").read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(builder, "HERE", tmp_path)
    monkeypatch.setattr(builder, "build", lambda: catalog)
    builder.write()
    first = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    builder.write()
    assert first == {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    html = (tmp_path / "review.html").read_text(encoding="utf-8")
    assert "</script><script>throw" not in html
    assert "\\u003c/script>" in html
    assert "__CATALOG__" not in html and "__UNKNOWN_COUNT__" not in html


def test_runtime_observations_cover_catalog_without_claiming_live_audio_accuracy():
    audit = json.loads((HERE / "observations.json").read_text(encoding="utf-8"))
    catalog = builder.build()
    expected = {(entry["id"], language) for entry in catalog["entries"] for language in catalog["languages"]}
    assert {(row["id"], row["language"]) for row in audit["observations"]} == expected
    assert audit["counts"]["turns"] == len(expected)
    assert "No live STT/TTS/model/carrier requests" in audit["scope"]
    assert "do not establish semantic correctness" in audit["interpretation"]
    assert not any(row["flags"] and "unexpected_proposal_or_booking" in row["flags"] for row in audit["observations"])
