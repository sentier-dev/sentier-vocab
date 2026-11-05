import pytest

from sentier_vocab import paths
from sentier_vocab.schema import expand_curie, load_relation_schema, load_term_schema

SKOS = "http://www.w3.org/2004/02/skos/core#"
ONT = "https://vocab.sentier.dev/ontology/"


def test_term_schema_columns_in_order():
    schema = load_term_schema(paths.TERM_SCHEMA)
    assert list(schema.columns) == [
        "iri",
        "type",
        "pref_label",
        "alt_labels",
        "definition",
        "notation",
        "additional_notations",
        "source",
        "status",
        "attributes",
    ]
    assert schema.columns["pref_label"].predicate == SKOS + "prefLabel"
    assert schema.columns["pref_label"].lang == "en"
    assert schema.columns["notation"].lang is None
    assert schema.columns["iri"].required and schema.columns["iri"].unique


def test_term_types_carry_namespace_category_class_and_attributes():
    schema = load_term_schema(paths.TERM_SCHEMA)
    flow = schema.types["elementary-flow"]
    assert flow.category == "flows"
    assert flow.namespace == "https://vocab.sentier.dev/flows/"
    assert flow.class_uri == SKOS + "Concept"
    assert flow.attributes["compartment"].predicate == ONT + "compartment"
    assert flow.attributes["compartment"].type == "string"
    process = schema.types["process"]
    assert process.class_uri == ONT + "Process"
    assert process.attributes["valid_from"].type == "date"
    assert process.attributes["process_type"].enum == ("unit", "system", "lci_result")
    assert schema.types["source"].attributes["creators"].type == "list[string]"
    assert schema.types["characterization-factor"].retired is True
    assert schema.types["elementary-flow"].retired is False


def test_relation_schema_predicates():
    schema = load_relation_schema(paths.RELATION_SCHEMA)
    assert list(schema.columns) == ["subject", "predicate", "object", "source", "status"]
    broader = schema.predicates["skos:broader"]
    assert broader.uri == SKOS + "broader"
    assert broader.subject == ("any",) and broader.object == ("any",)
    unit = schema.predicates["qudt:hasUnit"]
    assert "elementary-flow" in unit.subject
    assert unit.object == ("unit",)
    assert unit.external == ("http://qudt.org/vocab/unit/",)
    assert unit.max_one_per_subject is True
    assert schema.predicates["skos:related"].max_one_per_subject is False


def test_expand_curie():
    prefixes = {"skos": SKOS}
    assert expand_curie(prefixes, "skos:broader") == SKOS + "broader"
    assert expand_curie(prefixes, "https://x/y") == "https://x/y"
    with pytest.raises(KeyError):
        expand_curie(prefixes, "nope:thing")


def test_schema_rejects_unknown_attribute_type(tmp_path):
    bad = tmp_path / "term.yaml"
    bad.write_text(
        "version: 1.0.0\nprefixes: {ont: 'https://vocab.sentier.dev/ontology/'}\n"
        "columns:\n  iri: {type: string, required: true}\n"
        "types:\n  thing:\n    category: things\n    namespace: https://vocab.sentier.dev/things/\n"
        "    attributes:\n      x: {predicate: ont:x, type: blob}\n"
    )
    with pytest.raises(ValueError, match="blob"):
        load_term_schema(bad)
