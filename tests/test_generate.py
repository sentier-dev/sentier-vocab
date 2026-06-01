from rdflib import Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SKOS

from sentier_vocab import paths
from sentier_vocab.generate import build_graph, generate_category


def test_build_graph_produces_expected_triples():
    concepts = [
        {
            "iri": "https://vocab.sentier.dev/flows/X1",
            "pref_label": "Foo",
            "definition": "A foo.",
            "exact_match": ["http://example.org/X1"],
        }
    ]
    result = build_graph(concepts, "https://vocab.sentier.dev/flows/")

    expected = Graph()
    scheme = URIRef("https://vocab.sentier.dev/flows/")
    x1 = URIRef("https://vocab.sentier.dev/flows/X1")
    expected.add((scheme, RDF.type, SKOS.ConceptScheme))
    expected.add((x1, RDF.type, SKOS.Concept))
    expected.add((x1, SKOS.inScheme, scheme))
    expected.add((x1, SKOS.prefLabel, Literal("Foo", lang="en")))
    expected.add((x1, SKOS.definition, Literal("A foo.", lang="en")))
    expected.add((x1, SKOS.exactMatch, URIRef("http://example.org/X1")))

    assert isomorphic(result, expected)


def test_build_graph_handles_broader_and_alt_labels():
    concepts = [
        {
            "iri": "https://vocab.sentier.dev/flows/X2",
            "pref_label": "Bar",
            "alt_labels": ["Baz"],
            "broader": "https://vocab.sentier.dev/flows/X1",
        }
    ]
    result = build_graph(concepts, "https://vocab.sentier.dev/flows/")
    x2 = URIRef("https://vocab.sentier.dev/flows/X2")
    assert (x2, SKOS.altLabel, Literal("Baz", lang="en")) in result
    assert (x2, SKOS.broader, URIRef("https://vocab.sentier.dev/flows/X1")) in result


def test_build_graph_handles_notation_close_match_related():
    concepts = [
        {
            "iri": "https://vocab.sentier.dev/flows/X3",
            "pref_label": "Qux",
            "notation": "Q3",
            "close_match": ["http://example.org/close"],
            "related": ["http://example.org/rel"],
        }
    ]
    result = build_graph(concepts, "https://vocab.sentier.dev/flows/")
    x3 = URIRef("https://vocab.sentier.dev/flows/X3")
    # notation is a plain literal (NOT language-tagged)
    assert (x3, SKOS.notation, Literal("Q3")) in result
    assert (x3, SKOS.closeMatch, URIRef("http://example.org/close")) in result
    assert (x3, SKOS.related, URIRef("http://example.org/rel")) in result


def test_generate_category_rejects_unregistered_scheme(tmp_path):
    import pytest
    from sentier_vocab.errors import SchemaValidationError
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "scheme: https://vocab.sentier.dev/NOT-A-REAL-NS/\n"
        "flows:\n"
        "  - iri: https://vocab.sentier.dev/NOT-A-REAL-NS/X\n"
        "    pref_label: X\n"
        "    status: published\n"
    )
    with pytest.raises(SchemaValidationError):
        generate_category(
            category="elementary-flows",
            schema_path=paths.SCHEMAS_DIR / "elementary-flow.yaml",
            data_path=bad,
            output_path=tmp_path / "out.ttl",
        )


def test_generate_category_writes_valid_ttl(tmp_path):
    out = tmp_path / "flows.ttl"
    result_path = generate_category(
        category="elementary-flows",
        schema_path=paths.SCHEMAS_DIR / "elementary-flow.yaml",
        data_path=paths.DATA_DIR / "elementary-flows" / "water.yaml",
        output_path=out,
    )
    assert result_path == out
    assert out.exists()
    # Re-parse the emitted TTL and confirm the freshwater concept is present.
    reparsed = Graph().parse(out, format="turtle")
    freshwater = URIRef("https://vocab.sentier.dev/flows/ENVO_00002006")
    assert (freshwater, RDF.type, SKOS.Concept) in reparsed
    assert (freshwater, SKOS.prefLabel, Literal("Freshwater", lang="en")) in reparsed
