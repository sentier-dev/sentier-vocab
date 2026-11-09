from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS, XSD
from tests.conftest import CORE, FLOWS, KG, MASS

from sentier_vocab import paths
from sentier_vocab.generate import (
    build_graphs,
    generate,
    output_name,
    relation_triple,
    term_triples,
)
from sentier_vocab.layers import load_relations, load_terms
from sentier_vocab.schema import load_relation_schema, load_term_schema

ONT = "https://vocab.sentier.dev/ontology/"
QUDT = "http://qudt.org/schema/qudt/"
DCT = "http://purl.org/dc/terms/"


def test_term_triples_for_a_flow():
    schema = load_term_schema(paths.TERM_SCHEMA)
    row = {
        "iri": FLOWS + "X1",
        "type": "elementary-flow",
        "pref_label": "Foo",
        "definition": "A foo.",
        "alt_labels": ["Bar"],
        "notation": "X1",
        "additional_notations": ["ec:1"],
        "source": CORE,
        "status": "draft",
        "attributes": {"compartment": "air", "cas_number": "1-2-3"},
    }
    t = set(term_triples(row, schema))
    s = URIRef(FLOWS + "X1")
    assert (s, RDF.type, SKOS.Concept) in t
    assert (s, SKOS.inScheme, URIRef(FLOWS)) in t
    assert (s, SKOS.prefLabel, Literal("Foo", lang="en")) in t
    assert (s, SKOS.altLabel, Literal("Bar", lang="en")) in t
    assert (s, SKOS.definition, Literal("A foo.", lang="en")) in t
    assert (s, SKOS.notation, Literal("X1")) in t
    assert (s, SKOS.notation, Literal("ec:1")) in t
    assert (s, URIRef(DCT + "source"), URIRef(CORE)) in t
    assert (s, URIRef(ONT + "compartment"), Literal("air")) in t
    assert (s, URIRef(ONT + "casNumber"), Literal("1-2-3")) in t
    assert not any(o == Literal("draft") for _, _, o in t)  # status is internal


def test_term_triples_datatypes_and_class():
    schema = load_term_schema(paths.TERM_SCHEMA)
    row = {
        "iri": "https://vocab.sentier.dev/processes/p",
        "type": "process",
        "pref_label": "P",
        "source": CORE,
        "attributes": {"valid_from": "2020-01-01", "technology": "BOF", "process_type": "unit"},
    }
    t = set(term_triples(row, schema))
    s = URIRef(row["iri"])
    assert (s, RDF.type, URIRef(ONT + "Process")) in t
    assert (s, URIRef(ONT + "validFrom"), Literal("2020-01-01", datatype=XSD.date)) in t
    assert (s, URIRef(ONT + "technology"), Literal("BOF", lang="en")) in t
    assert (s, URIRef(ONT + "processType"), Literal("unit")) in t
    ic = {
        "iri": "https://vocab.sentier.dev/impact-categories/c",
        "type": "impact-category",
        "pref_label": "C",
        "source": CORE,
        "attributes": {"normalization_factor": 1.0},
    }
    nf = URIRef(ONT + "normalizationFactor")
    assert (URIRef(ic["iri"]), nf, Literal(1.0)) in set(term_triples(ic, schema))
    src = {
        "iri": CORE,
        "type": "source",
        "pref_label": "S",
        "source": CORE,
        "attributes": {"creators": ["A", "B"], "date": "2021-08-09"},
    }
    ts = set(term_triples(src, schema))
    assert (URIRef(CORE), URIRef(DCT + "creator"), Literal("A")) in ts
    assert (URIRef(CORE), URIRef(DCT + "creator"), Literal("B")) in ts
    assert (URIRef(CORE), URIRef(DCT + "date"), Literal("2021-08-09", datatype=XSD.date)) in ts
    contact = {
        "iri": "https://vocab.sentier.dev/contacts/c",
        "type": "contact",
        "pref_label": "C",
        "source": CORE,
        "attributes": {"url": "https://sentier.dev"},
    }
    tc = set(term_triples(contact, schema))
    assert (URIRef(contact["iri"]), URIRef(ONT + "url"), URIRef("https://sentier.dev")) in tc


def test_relation_triple():
    rel_schema = load_relation_schema(paths.RELATION_SCHEMA)
    row = {"subject": FLOWS + "a", "predicate": "qudt:hasUnit", "object": KG, "source": CORE}
    assert relation_triple(row, rel_schema) == (
        URIRef(FLOWS + "a"),
        URIRef(QUDT + "hasUnit"),
        URIRef(KG),
    )


def test_output_name():
    assert output_name("flows", "sentier-core") == "flows.ttl"
    assert output_name("flows", "ef-3.1-03") == "flows.ef-3.1-03.ttl"


def test_build_graphs_groups_by_category_and_file(layout):
    terms_dir, relations_dir = layout
    graphs = build_graphs(load_terms(terms_dir), load_relations(relations_dir))
    assert set(graphs) == {
        ("sources", "sentier-core"),
        ("flows", "sentier-core"),
        ("unit-groups", "sentier-core"),
        ("processes", "sentier-core"),
        ("sources", "ef-3.1"),
        ("flows", "ef-3.1"),
    }
    flows = graphs[("flows", "sentier-core")]
    assert (URIRef(FLOWS), RDF.type, SKOS.ConceptScheme) in flows
    assert (
        URIRef(FLOWS + "ENVO_00002010"),
        SKOS.broader,
        URIRef(FLOWS + "ENVO_00002006"),
    ) in flows
    # a relation lands in the graph of its subject
    assert (URIRef(MASS), URIRef(QUDT + "hasUnit"), URIRef(KG)) in graphs[
        ("unit-groups", "sentier-core")
    ]


def test_generate_writes_ttl_files(layout, tmp_path):
    terms_dir, relations_dir = layout
    out = tmp_path / "out"
    written = generate(terms_dir, relations_dir, out)
    names = sorted(p.name for p in written)
    assert names == [
        "flows.ef-3.1.ttl",
        "flows.ttl",
        "processes.ttl",
        "sources.ef-3.1.ttl",
        "sources.ttl",
        "unit-groups.ttl",
    ]
    g = Graph().parse(out / "flows.ttl", format="turtle")
    assert (URIRef(FLOWS + "ENVO_00002006"), SKOS.prefLabel, Literal("Freshwater", lang="en")) in g
    first = (out / "flows.ttl").read_bytes()
    generate(terms_dir, relations_dir, out)
    assert (out / "flows.ttl").read_bytes() == first
