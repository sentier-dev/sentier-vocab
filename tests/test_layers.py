import pyarrow.parquet as pq
import pytest

from sentier_vocab.layers import (
    MAX_FILE_BYTES,
    RELATION_SCHEMA,
    TERM_SCHEMA,
    load_relations,
    load_terms,
    read_rows,
    release_of,
    write_relations,
    write_terms,
)

SRC = "https://vocab.sentier.dev/sources/sentier-core"


def _term(iri, type_="elementary-flow", **extra):
    row = {
        "iri": iri,
        "type": type_,
        "pref_label": iri.rsplit("/", 1)[1],
        "source": SRC,
        "status": "draft",
    }
    row.update(extra)
    return row


def test_write_terms_sorts_and_serialises_attributes(tmp_path):
    rows = [
        _term(
            "https://vocab.sentier.dev/flows/b",
            attributes={"formula": "H2O", "compartment": "water"},
        ),
        _term("https://vocab.sentier.dev/flows/a", alt_labels=["x"]),
        _term("https://vocab.sentier.dev/contacts/z", type_="contact"),
    ]
    files = write_terms(rows, tmp_path, "sentier-core")
    assert files == [tmp_path / "sentier-core.parquet"]
    table = pq.read_table(files[0])
    assert table.schema.equals(TERM_SCHEMA)
    out = table.to_pylist()
    assert [r["iri"] for r in out] == [
        "https://vocab.sentier.dev/contacts/z",
        "https://vocab.sentier.dev/flows/a",
        "https://vocab.sentier.dev/flows/b",
    ]
    assert out[2]["attributes"] == '{"compartment": "water", "formula": "H2O"}'
    assert out[1]["attributes"] is None


def test_read_rows_strips_nulls_and_parses_attributes(tmp_path):
    write_terms(
        [_term("https://vocab.sentier.dev/flows/a", attributes={"formula": "X"})], tmp_path, "r"
    )
    rows = read_rows(tmp_path / "r.parquet")
    assert rows == [
        {
            "iri": "https://vocab.sentier.dev/flows/a",
            "type": "elementary-flow",
            "pref_label": "a",
            "source": SRC,
            "status": "draft",
            "attributes": {"formula": "X"},
        }
    ]


def test_write_terms_shards_when_over_limit(tmp_path, monkeypatch):
    import sentier_vocab.layers as layers

    monkeypatch.setattr(layers, "MAX_FILE_BYTES", 6000)
    rows = [
        _term(f"https://vocab.sentier.dev/flows/{i:05d}", definition="d" * 200) for i in range(400)
    ]
    files = write_terms(rows, tmp_path, "big")
    assert len(files) > 1
    assert files[0].name == "big-01.parquet"
    assert all(f.stat().st_size <= 6000 for f in files)
    assert sum(len(read_rows(f)) for f in files) == 400
    last = None
    for f in files:
        for row in read_rows(f):
            assert last is None or row["iri"] > last
            last = row["iri"]


def test_write_and_load_relations(tmp_path):
    rows = [
        {
            "subject": "s2",
            "predicate": "skos:broader",
            "object": "o",
            "source": SRC,
            "status": "draft",
        },
        {
            "subject": "s1",
            "predicate": "skos:broader",
            "object": "o",
            "source": SRC,
            "status": "draft",
        },
    ]
    files = write_relations(rows, tmp_path, "sentier-core")
    assert pq.read_table(files[0]).schema.equals(RELATION_SCHEMA)
    loaded = load_relations(tmp_path)
    assert list(loaded) == [tmp_path / "sentier-core.parquet"]
    assert [r["subject"] for r in loaded[files[0]]] == ["s1", "s2"]


def test_load_terms_returns_sorted_mapping(tmp_path):
    write_terms([_term("https://vocab.sentier.dev/flows/a")], tmp_path, "b")
    write_terms([_term("https://vocab.sentier.dev/flows/c")], tmp_path, "a")
    assert [p.name for p in load_terms(tmp_path)] == ["a.parquet", "b.parquet"]


def test_release_of():
    assert release_of("ef-3.1-03.parquet") == "ef-3.1"
    assert release_of("ef-3.1.parquet") == "ef-3.1"
    assert release_of("bafu-2026.parquet") == "bafu-2026"
    assert release_of("sentier-core-10.parquet") == "sentier-core"


def test_write_terms_rejects_unknown_column(tmp_path):
    with pytest.raises(ValueError, match="compartment"):
        write_terms([_term("https://vocab.sentier.dev/flows/a", compartment="air")], tmp_path, "r")


def test_max_file_bytes_is_under_pre_commit_guard():
    assert MAX_FILE_BYTES < 3000 * 1024
