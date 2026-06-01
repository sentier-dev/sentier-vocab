import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, SKOS

from sentier_vocab import paths
from sentier_vocab.errors import SchemaValidationError
from sentier_vocab.rdf_mapping import concept_to_triples, member_slot_and_class, schema_view

FLAT = str(paths.REPO_ROOT / "tests" / "fixtures" / "engine" / "flat.yaml")
SCHEME = "https://vocab.sentier.dev/flows/"
ONT = "https://vocab.sentier.dev/ontology/"
QUDT = "http://qudt.org/schema/qudt/"


def _triples(record):
    return set(concept_to_triples(record, "Thing", schema_view(FLAT), SCHEME))


def test_type_and_scheme_emitted():
    s = URIRef("https://vocab.sentier.dev/flows/X")
    t = _triples({"iri": str(s), "label": "X"})
    assert (s, RDF.type, URIRef(ONT + "Thing")) in t
    assert (s, SKOS.inScheme, URIRef(SCHEME)) in t


def test_lang_literal_and_plain_and_typed_and_ref_and_multivalued():
    s = URIRef("https://vocab.sentier.dev/flows/X")
    t = _triples(
        {
            "iri": str(s),
            "label": "Water",
            "code": "W",
            "ratio": 0.5,
            "unit": "http://qudt.org/vocab/unit/KiloGM",
            "tags": ["a", "b"],
        }
    )
    assert (s, SKOS.prefLabel, Literal("Water", lang="en")) in t
    assert (s, SKOS.notation, Literal("W")) in t
    assert (s, URIRef(ONT + "ratio"), Literal(0.5)) in t
    assert (s, URIRef(QUDT + "hasUnit"), URIRef("http://qudt.org/vocab/unit/KiloGM")) in t
    assert (s, URIRef(ONT + "tag"), Literal("a")) in t
    assert (s, URIRef(ONT + "tag"), Literal("b")) in t


def test_internal_slot_is_not_serialized():
    s = URIRef("https://vocab.sentier.dev/flows/X")
    t = _triples({"iri": str(s), "label": "X", "secret": "hidden"})
    assert all(o != Literal("hidden") for (_, _, o) in t)


def test_missing_slot_uri_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "id: https://vocab.sentier.dev/schemas/_bad\n"
        "name: bad\n"
        "prefixes: {linkml: 'https://w3id.org/linkml/', sentier: 'https://vocab.sentier.dev/'}\n"
        "default_prefix: sentier\ndefault_range: string\nimports: [linkml:types]\n"
        "classes:\n  T:\n    tree_root: true\n    attributes:\n"
        "      iri: {identifier: true, range: uriorcurie}\n"
        "      oops: {}\n"
    )
    with pytest.raises(SchemaValidationError):
        concept_to_triples(
            {"iri": "https://vocab.sentier.dev/flows/Y", "oops": "v"},
            "T",
            schema_view(str(bad)),
            SCHEME,
        )


def test_expand_passes_through_full_uri_slot_uri(tmp_path):
    schema = tmp_path / "fulluri.yaml"
    schema.write_text(
        "id: https://vocab.sentier.dev/schemas/_fulluri\n"
        "name: fulluri\n"
        "prefixes: {linkml: 'https://w3id.org/linkml/', sentier: 'https://vocab.sentier.dev/'}\n"
        "default_prefix: sentier\ndefault_range: string\nimports: [linkml:types]\n"
        "classes:\n  T:\n    tree_root: true\n    attributes:\n"
        "      iri: {identifier: true, range: uriorcurie}\n"
        "      note: {slot_uri: 'http://www.w3.org/2004/02/skos/core#note'}\n"
    )
    s = URIRef("https://vocab.sentier.dev/flows/Z")
    t = set(
        concept_to_triples({"iri": str(s), "note": "hi"}, "T", schema_view(str(schema)), SCHEME)
    )
    assert (s, URIRef("http://www.w3.org/2004/02/skos/core#note"), Literal("hi")) in t


NESTED = str(paths.REPO_ROOT / "tests" / "fixtures" / "engine" / "nested.yaml")


def test_inlined_objects_mint_child_iris_and_link():
    p = URIRef("https://vocab.sentier.dev/processes/steel")
    flow = "https://vocab.sentier.dev/flows/ENVO_iron"
    t = set(
        concept_to_triples(
            {
                "iri": str(p),
                "exchanges": [{"flow": flow, "direction": "input", "amount": 2.3}],
            },
            "Parent",
            schema_view(NESTED),
            "https://vocab.sentier.dev/processes/",
        )
    )
    child = URIRef("https://vocab.sentier.dev/processes/steel/exchanges/ENVO_iron-input")
    assert (p, URIRef(ONT + "hasExchange"), child) in t
    assert (child, RDF.type, URIRef(ONT + "Exchange")) in t
    assert (child, URIRef(ONT + "flow"), URIRef(flow)) in t
    assert (child, URIRef(ONT + "amount"), Literal(2.3)) in t


def test_member_slot_and_class_resolves_tree_root_member():
    assert member_slot_and_class(schema_view(NESTED)) == ("exchanges", "Exchange")


def test_member_slot_and_class_raises_without_member(tmp_path):
    schema = tmp_path / "nocoll.yaml"
    schema.write_text(
        "id: https://vocab.sentier.dev/schemas/_nocoll\n"
        "name: nocoll\n"
        "prefixes: {linkml: 'https://w3id.org/linkml/', sentier: 'https://vocab.sentier.dev/'}\n"
        "default_prefix: sentier\ndefault_range: string\nimports: [linkml:types]\n"
        "classes:\n  Solo:\n    tree_root: true\n    attributes:\n"
        "      iri: {identifier: true, range: uriorcurie}\n"
        "      label: {slot_uri: 'http://www.w3.org/2004/02/skos/core#prefLabel'}\n"
    )
    with pytest.raises(SchemaValidationError):
        member_slot_and_class(schema_view(str(schema)))


def test_same_flow_both_directions_mints_distinct_children():
    p = URIRef("https://vocab.sentier.dev/processes/mill")
    flow = "https://vocab.sentier.dev/flows/ENVO_water"
    t = set(
        concept_to_triples(
            {
                "iri": str(p),
                "exchanges": [
                    {"flow": flow, "direction": "input", "amount": 1.0},
                    {"flow": flow, "direction": "output", "amount": 0.4},
                ],
            },
            "Parent",
            schema_view(NESTED),
            "https://vocab.sentier.dev/processes/",
        )
    )
    child_in = URIRef("https://vocab.sentier.dev/processes/mill/exchanges/ENVO_water-input")
    child_out = URIRef("https://vocab.sentier.dev/processes/mill/exchanges/ENVO_water-output")
    assert (p, URIRef(ONT + "hasExchange"), child_in) in t
    assert (p, URIRef(ONT + "hasExchange"), child_out) in t
    assert child_in != child_out
