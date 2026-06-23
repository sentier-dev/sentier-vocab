"""Tests for format-agnostic source loading (YAML + Parquet) and round-trip fidelity."""

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import yaml as _yaml

from sentier_vocab import paths
from sentier_vocab.errors import SchemaValidationError
from sentier_vocab.generate import generate_sources
from sentier_vocab.loaders import _strip_empty, arrow_schema_for, dump_parquet, load_source
from sentier_vocab.rdf_mapping import member_slot_and_class, schema_view

ORG_SCHEMA = paths.SCHEMAS_DIR / "organism.yaml"
SCHEME = "https://vocab.sentier.dev/organisms/"

RECORDS = [
    {
        "iri": SCHEME + "A001",
        "pref_label": "Alpha",
        "definition": "First.",
        "notation": "A001",
        "alt_labels": ["a", "alpha"],
        "related": [SCHEME + "A002"],
        "status": "draft",
    },
    {
        "iri": SCHEME + "A002",
        "pref_label": "Beta",  # no alt_labels / related -> exercises optional omission
        "notation": "A002",
        "status": "draft",
    },
]


def test_strip_empty_drops_none_and_empty_list():
    assert _strip_empty({"a": 1, "b": None, "c": [], "d": ["x"]}) == {"a": 1, "d": ["x"]}


def test_arrow_schema_scalar_and_list_types():
    sv = schema_view(str(ORG_SCHEMA))
    _, class_name = member_slot_and_class(sv)
    schema = arrow_schema_for(sv, class_name)
    fields = {f.name: f.type for f in schema}
    assert fields["pref_label"] == pa.string()
    assert fields["alt_labels"] == pa.list_(pa.string())
    assert "scheme" not in fields  # internal slot -> stored as metadata, not a column


def test_parquet_round_trip_omits_absent_optionals(tmp_path):
    sv = schema_view(str(ORG_SCHEMA))
    items_key, class_name = member_slot_and_class(sv)
    path = tmp_path / "foodex2.parquet"
    dump_parquet(SCHEME, RECORDS, arrow_schema_for(sv, class_name), path)

    scheme, records = load_source(path, items_key)
    assert scheme == SCHEME
    by_iri = {r["iri"]: r for r in records}
    # absent optionals must NOT reappear as None/[] (keystone for byte-identical TTL)
    assert "alt_labels" not in by_iri[SCHEME + "A002"]
    assert "related" not in by_iri[SCHEME + "A002"]
    assert by_iri[SCHEME + "A001"]["alt_labels"] == ["a", "alpha"]


def test_parquet_scheme_lives_in_metadata(tmp_path):
    sv = schema_view(str(ORG_SCHEMA))
    _, class_name = member_slot_and_class(sv)
    path = tmp_path / "foodex2.parquet"
    dump_parquet(SCHEME, RECORDS, arrow_schema_for(sv, class_name), path)
    meta = pq.read_table(path).schema.metadata
    assert meta[b"scheme"].decode() == SCHEME


def test_parquet_missing_scheme_metadata_raises(tmp_path):
    path = tmp_path / "no_scheme.parquet"
    pq.write_table(pa.table({"iri": [SCHEME + "X"], "pref_label": ["X"]}), path)
    with pytest.raises(SchemaValidationError, match="scheme"):
        load_source(path, "organisms")


def test_unsupported_format_raises(tmp_path):
    bad = tmp_path / "data.csv"
    bad.write_text("iri,pref_label\n")
    with pytest.raises(SchemaValidationError, match="unsupported source format"):
        load_source(bad, "organisms")


def test_generate_from_yaml_and_parquet_byte_identical(tmp_path):
    """The core contract: a category generated from Parquet == from the equivalent YAML."""
    sv = schema_view(str(ORG_SCHEMA))
    items_key, class_name = member_slot_and_class(sv)

    yaml_src = tmp_path / "core.yaml"
    yaml_src.write_text(_yaml.safe_dump({"scheme": SCHEME, items_key: RECORDS}))
    pq_src = tmp_path / "foodex2.parquet"
    dump_parquet(SCHEME, RECORDS, arrow_schema_for(sv, class_name), pq_src)

    out_yaml = generate_sources(ORG_SCHEMA, [yaml_src], tmp_path / "from_yaml.ttl")
    out_pq = generate_sources(ORG_SCHEMA, [pq_src], tmp_path / "from_parquet.ttl")
    assert out_yaml.read_bytes() == out_pq.read_bytes()


def test_generate_rejects_conflicting_schemes(tmp_path):
    sv = schema_view(str(ORG_SCHEMA))
    items_key, _ = member_slot_and_class(sv)
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(_yaml.safe_dump({"scheme": SCHEME, items_key: [RECORDS[0]]}))
    b.write_text(
        _yaml.safe_dump({"scheme": "https://vocab.sentier.dev/products/", items_key: [RECORDS[1]]})
    )
    with pytest.raises(SchemaValidationError, match="conflicting schemes|registered"):
        generate_sources(ORG_SCHEMA, [a, b], tmp_path / "out.ttl")
