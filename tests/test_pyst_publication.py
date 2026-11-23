"""The PyST publication plan: terms and relations -> the documents PyST accepts."""

from pathlib import Path

import pytest

from sentier_vocab import paths
from sentier_vocab.layers import load_relations, load_terms
from sentier_vocab.pyst.publication import (
    BIBO_STATUS,
    PlanError,
    api_path,
    build_plan,
    load_config,
)

SKOS = "http://www.w3.org/2004/02/skos/core#"
ONT = "https://vocab.sentier.dev/ontology/"
DCT = "http://purl.org/dc/terms/"
SRC = "https://vocab.sentier.dev/sources/demo"
ORG = "https://vocab.sentier.dev/organisms/"
PROD = "https://vocab.sentier.dev/products/"
ORG_SCHEME = "https://vocab.sentier.dev/schemes/demo/organisms"
PROD_SCHEME = "https://vocab.sentier.dev/schemes/demo/products"
UNITS = "https://vocab.sentier.dev/units/"

CONFIG = {
    "status": {"draft": "draft", "published": "accepted", "deprecated": "rejected"},
    "schemes": [
        {
            "iri": ORG_SCHEME,
            "label": "Demo organisms",
            "definition": "Organisms of the demo release.",
            "version": "1",
            "created": "2026-11-20",
            "creator": "https://example.org/",
            "select": [{"release": "demo", "types": ["organism"]}],
        },
        {
            "iri": PROD_SCHEME,
            "label": "Demo products",
            "definition": "Products of the demo release.",
            "version": "1",
            "created": "2026-11-20",
            "creator": "https://example.org/",
            "select": [{"release": "demo", "types": ["product"]}],
        },
        {
            "iri": UNITS,
            "existing": True,
            "select": [{"release": "demo", "types": ["unit"]}],
        },
    ],
    "skip": [{"release": "demo", "types": ["source"]}],
}


def term(iri, type_, label, **extra):
    return {
        "iri": iri,
        "type": type_,
        "pref_label": label,
        "source": SRC,
        "status": "draft",
        **extra,
    }


def demo_terms():
    return {
        Path("terms/demo.parquet"): [
            term(SRC, "source", "Demo", status="published"),
            term(ORG + "animal", "organism", "Animal", status="published"),
            term(
                ORG + "cow",
                "organism",
                "Cow",
                alt_labels=["Cattle"],
                definition="A bovine.",
                notation="A1",
                additional_notations=["x:1"],
            ),
            term(ORG + "old", "organism", "Old", status="deprecated"),
            term(PROD + "milk", "product", "Milk", attributes={"cpc_code": "0221"}),
            term(UNITS + "unit/M2-YR", "unit", "Square metre year"),
        ]
    }


def rel(subject, predicate, obj):
    return {"subject": subject, "predicate": predicate, "object": obj, "source": SRC}


def demo_relations():
    return {
        Path("relations/demo.parquet"): [
            rel(ORG + "cow", "skos:broader", ORG + "animal"),
            rel(PROD + "milk", "skos:broader", ORG + "cow"),
            rel(PROD + "milk", "skos:related", ORG + "animal"),
        ]
    }


@pytest.fixture
def plan():
    return build_plan(demo_terms(), demo_relations(), CONFIG)


def by_iri(scheme):
    return {doc["@id"]: doc for doc in scheme.concepts}


def test_terms_are_grouped_into_the_configured_schemes(plan):
    assert [(s.iri, len(s.concepts)) for s in plan.schemes] == [
        (ORG_SCHEME, 3),
        (PROD_SCHEME, 1),
        (UNITS, 1),
    ]
    assert plan.skipped_terms == 1


def test_an_existing_scheme_is_never_created(plan):
    units = plan.schemes[2]
    assert units.existing and units.document is None
    assert units.concepts[0][SKOS + "inScheme"] == [{"@id": UNITS}]


def test_scheme_document_carries_what_pyst_requires(plan):
    doc = plan.schemes[0].document
    assert doc["@type"] == [SKOS + "ConceptScheme"]
    assert doc[SKOS + "prefLabel"] == [{"@value": "Demo organisms", "@language": "en"}]
    assert doc[SKOS + "definition"][0]["@value"] == "Organisms of the demo release."
    assert doc["http://www.w3.org/2002/07/owl#versionInfo"] == [{"@value": "1"}]
    assert doc[DCT + "created"][0]["@value"] == "2026-11-20"
    assert doc[DCT + "creator"] == [{"@id": "https://example.org/"}]
    assert doc["http://purl.org/ontology/bibo/status"] == [{"@id": BIBO_STATUS + "draft"}]


def test_concept_document(plan):
    cow = by_iri(plan.schemes[0])[ORG + "cow"]
    assert cow["@type"] == [SKOS + "Concept"]
    assert cow[SKOS + "inScheme"] == [{"@id": ORG_SCHEME}]
    assert cow[SKOS + "prefLabel"] == [{"@value": "Cow", "@language": "en"}]
    assert cow[SKOS + "altLabel"] == [{"@value": "Cattle", "@language": "en"}]
    assert cow[SKOS + "definition"] == [{"@value": "A bovine.", "@language": "en"}]
    assert [n["@value"] for n in cow[SKOS + "notation"]] == ["A1", "x:1"]
    assert cow[DCT + "source"] == [{"@id": SRC}]


def test_status_is_translated(plan):
    docs = by_iri(plan.schemes[0])
    status = "http://purl.org/ontology/bibo/status"
    assert docs[ORG + "cow"][status] == [{"@id": BIBO_STATUS + "draft"}]
    assert docs[ORG + "animal"][status] == [{"@id": BIBO_STATUS + "accepted"}]
    assert docs[ORG + "old"][status] == [{"@id": BIBO_STATUS + "rejected"}]


def test_top_concepts_are_those_without_a_broader_term_in_their_scheme(plan):
    organisms, products = by_iri(plan.schemes[0]), by_iri(plan.schemes[1])
    top = SKOS + "topConceptOf"
    assert organisms[ORG + "animal"][top] == [{"@id": ORG_SCHEME}]
    assert top not in organisms[ORG + "cow"]
    # milk's only broader term is in another scheme, so it tops its own scheme
    assert products[PROD + "milk"][top] == [{"@id": PROD_SCHEME}]


def test_a_flat_scheme_above_the_limit_lists_no_top_concepts():
    plan = build_plan(demo_terms(), demo_relations(), {**CONFIG, "top_concept_limit": 1})
    organisms, products = plan.schemes[0], plan.schemes[1]
    top = SKOS + "topConceptOf"
    assert not any(top in doc for doc in organisms.concepts)  # two roots, limit one
    assert top in products.concepts[0]  # one root


def test_terms_added_to_an_existing_scheme_are_not_top_concepts(plan):
    assert SKOS + "topConceptOf" not in plan.schemes[2].concepts[0]


def test_broader_stays_in_scheme_and_becomes_broad_match_across_schemes(plan):
    assert list(plan.relationships) == [
        {"@id": ORG + "cow", SKOS + "broader": [{"@id": ORG + "animal"}]},
        {"@id": PROD + "milk", SKOS + "broadMatch": [{"@id": ORG + "cow"}]},
    ]


def test_other_relations_and_attributes_are_properties_of_the_concept(plan):
    milk = by_iri(plan.schemes[1])[PROD + "milk"]
    assert milk[SKOS + "related"] == [{"@id": ORG + "animal"}]
    assert milk[ONT + "cpcCode"] == [{"@value": "0221"}]


def test_process_keeps_its_class_and_gains_skos_concept():
    config = {
        **CONFIG,
        "schemes": [
            {**CONFIG["schemes"][0], "select": [{"release": "demo", "types": ["process"]}]}
        ],
    }
    terms = {
        Path("terms/demo.parquet"): [
            term(SRC, "source", "Demo"),
            term(
                "https://vocab.sentier.dev/processes/p1",
                "process",
                "Steel making",
                attributes={"valid_from": "2020-01-01"},
            ),
        ]
    }
    doc = build_plan(terms, {}, config).schemes[0].concepts[0]
    assert doc["@type"] == [SKOS + "Concept", ONT + "Process"]
    assert doc[ONT + "validFrom"] == [
        {"@value": "2020-01-01", "@type": "http://www.w3.org/2001/XMLSchema#date"}
    ]


def test_a_type_of_a_release_that_no_scheme_or_skip_covers_is_an_error():
    config = {**CONFIG, "skip": []}
    with pytest.raises(PlanError, match="demo.*source"):
        build_plan(demo_terms(), demo_relations(), config)


def test_a_broader_term_that_is_not_published_is_an_error():
    relations = {Path("r.parquet"): [rel(ORG + "cow", "skos:broader", SRC)]}
    with pytest.raises(PlanError, match="not published"):
        build_plan(demo_terms(), relations, CONFIG)


def test_relations_of_a_skipped_subject_are_dropped():
    relations = {Path("r.parquet"): [rel(SRC, "skos:related", ORG + "cow")]}
    plan = build_plan(demo_terms(), relations, CONFIG)
    assert plan.dropped_relations == 1 and not plan.relationships


def test_api_path_quotes_the_iri():
    assert api_path("concepts", ORG + "cow") == (
        "/api/v1/concepts/https%3A//vocab.sentier.dev/organisms/cow"
    )
    assert api_path("relationships") == "/api/v1/relationships/"


def test_repo_config_covers_every_term_of_the_repo():
    """The committed config and the committed layers build a plan."""
    plan = build_plan(
        load_terms(paths.TERMS_DIR),
        load_relations(paths.RELATIONS_DIR),
        load_config(paths.PYST_CONFIG),
    )
    total = sum(len(s.concepts) for s in plan.schemes) + plan.skipped_terms
    assert total == sum(len(rows) for rows in load_terms(paths.TERMS_DIR).values())
    iris = [s.iri for s in plan.schemes]
    assert len(iris) == len(set(iris))
    pairs = [
        (r["@id"], next(v for k, v in r.items() if k != "@id")[0]["@id"])
        for r in plan.relationships
    ]
    assert len(pairs) == len(set(pairs))


def test_every_document_passes_pysts_own_request_models():
    req = pytest.importorskip("py_semantic_taxonomy.adapters.routers.request_dto")
    plan = build_plan(demo_terms(), demo_relations(), CONFIG)
    for scheme in plan.schemes:
        if scheme.document:
            req.ConceptScheme(**scheme.document)
        for doc in scheme.concepts:
            req.ConceptCreate(**doc)
    for doc in plan.relationships:
        req.Relationship(**doc)
