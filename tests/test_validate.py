import pytest
from tests.conftest import CORE, EF, FLOWS, KG, core_relations, core_terms, ef_terms

from sentier_vocab.errors import ValidationError
from sentier_vocab.layers import write_relations, write_terms
from sentier_vocab.validate import validate, validate_or_raise

CF = "https://vocab.sentier.dev/characterization-factors/x"


def test_valid_layout_has_no_errors(layout):
    assert validate(*layout) == []


def _rewrite(layout, release, terms=None, relations=None):
    terms_dir, relations_dir = layout
    if terms is not None:
        for p in terms_dir.glob(f"{release}*.parquet"):
            p.unlink()
        write_terms(terms, terms_dir, release)
    if relations is not None:
        for p in relations_dir.glob(f"{release}*.parquet"):
            p.unlink()
        write_relations(relations, relations_dir, release)


def test_unknown_type_and_namespace_mismatch(layout):
    rows = core_terms()
    rows[1]["type"] = "widget"
    rows[2]["iri"] = "https://vocab.sentier.dev/products/ENVO_00002010"
    _rewrite(layout, "sentier-core", terms=rows)
    errors = validate(*layout)
    assert any("widget" in e and "not a listed type" in e for e in errors)
    assert any("ENVO_00002010" in e and "namespace" in e for e in errors)


def test_retired_type_rejected(layout):
    extra = {"iri": CF, "type": "characterization-factor", "pref_label": "x", "source": CORE}
    _rewrite(layout, "sentier-core", terms=core_terms() + [extra])
    assert any("retired" in e for e in validate(*layout))


def test_required_columns_and_status_enum(layout):
    rows = core_terms()
    del rows[1]["pref_label"]
    rows[2]["status"] = "maybe"
    _rewrite(layout, "sentier-core", terms=rows)
    errors = validate(*layout)
    assert any("pref_label" in e and "required" in e for e in errors)
    assert any("maybe" in e for e in errors)


def test_attribute_keys_and_datatypes(layout):
    rows = core_terms()
    rows[1]["attributes"] = {"colour": "blue"}
    rows[4]["attributes"] = {"valid_from": "yesterday", "process_type": "magic"}
    _rewrite(layout, "sentier-core", terms=rows)
    errors = validate(*layout)
    assert any("colour" in e and "not declared" in e for e in errors)
    assert any("valid_from" in e and "date" in e for e in errors)
    assert any("magic" in e for e in errors)


def test_duplicate_iri_across_files(layout):
    _rewrite(layout, "ef-3.1", terms=ef_terms() + [dict(core_terms()[1], source=EF)])
    assert any("duplicate iri" in e for e in validate(*layout))


def test_relation_checks(layout):
    a, b = FLOWS + "ENVO_00002006", FLOWS + "ENVO_00002010"
    rels = core_relations() + [
        {"subject": a, "predicate": "ont:fancy", "object": b, "source": CORE},
        {"subject": FLOWS + "nope", "predicate": "skos:broader", "object": b, "source": CORE},
        {"subject": a, "predicate": "skos:broader", "object": FLOWS + "nope", "source": CORE},
        {"subject": a, "predicate": "ont:method", "object": b, "source": CORE},
        {
            "subject": a,
            "predicate": "skos:exactMatch",
            "object": "https://vocab.brightway.one/x",
            "source": CORE,
        },
    ]
    _rewrite(layout, "sentier-core", relations=rels)
    errors = validate(*layout)
    assert any("ont:fancy" in e and "not a listed predicate" in e for e in errors)
    assert any("subject" in e and FLOWS + "nope" in e for e in errors)
    assert any("object" in e and FLOWS + "nope" in e for e in errors)
    assert any("ont:method" in e and "elementary-flow" in e for e in errors)
    assert any("brightway" in e and "external" in e for e in errors)


def test_source_checks(layout):
    rows = core_terms()
    rows[2]["source"] = EF  # second source in the sentier-core file
    rows[3]["source"] = "https://vocab.sentier.dev/sources/ghost"
    _rewrite(layout, "sentier-core", terms=rows)
    errors = validate(*layout)
    assert any("one source per file" in e for e in errors)
    assert any("ghost" in e and "source" in e for e in errors)


def test_file_stem_must_match_source_identifier(layout):
    terms_dir, _ = layout
    write_terms(ef_terms(), terms_dir, "ef-wrong")
    assert any("ef-wrong" in e and "stem" in e for e in validate(*layout))


def test_max_one_unit_and_flow_identity(layout):
    a, b = FLOWS + "ENVO_00002006", FLOWS + "ENVO_00002010"
    gram = "http://qudt.org/vocab/unit/GM"
    rels = core_relations() + [
        {"subject": a, "predicate": "qudt:hasUnit", "object": KG, "source": CORE},
        {"subject": a, "predicate": "qudt:hasUnit", "object": gram, "source": CORE},
        {"subject": b, "predicate": "qudt:hasUnit", "object": gram, "source": CORE},
    ]
    rows = core_terms()
    # a keeps its first edge in sort order (GM), so b with GM shares the identity of a.
    rows[2]["pref_label"] = "Freshwater"
    _rewrite(layout, "sentier-core", terms=rows, relations=rels)
    errors = validate(*layout)
    assert any("more than one qudt:hasUnit" in e for e in errors)
    assert any("flow identity" in e and "Freshwater" in e for e in errors)


def test_flow_identity_ignores_flows_without_unit(layout):
    rows = core_terms()
    rows[2]["pref_label"] = "Freshwater"
    _rewrite(layout, "sentier-core", terms=rows)
    assert not any("flow identity" in e for e in validate(*layout))


def test_validate_or_raise(layout):
    validate_or_raise(*layout)
    rows = core_terms()
    rows[1]["type"] = "widget"
    _rewrite(layout, "sentier-core", terms=rows)
    with pytest.raises(ValidationError, match="widget"):
        validate_or_raise(*layout)
