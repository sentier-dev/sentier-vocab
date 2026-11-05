"""Shared fixtures: a small valid terms/ + relations/ layout."""

import pytest

from sentier_vocab.layers import write_relations, write_terms

CORE = "https://vocab.sentier.dev/sources/sentier-core"
EF = "https://vocab.sentier.dev/sources/ef-3.1"
FLOWS = "https://vocab.sentier.dev/flows/"
MASS = "https://vocab.sentier.dev/units/group/mass"
STEEL = "https://vocab.sentier.dev/processes/steel"
KG = "http://qudt.org/vocab/unit/KiloGM"


def core_terms():
    return [
        {
            "iri": CORE,
            "type": "source",
            "pref_label": "Sentier.dev curated terms",
            "source": CORE,
            "status": "published",
        },
        {
            "iri": FLOWS + "ENVO_00002006",
            "type": "elementary-flow",
            "pref_label": "Freshwater",
            "source": CORE,
            "status": "published",
            "attributes": {"compartment": "water"},
        },
        {
            "iri": FLOWS + "ENVO_00002010",
            "type": "elementary-flow",
            "pref_label": "Saline water",
            "source": CORE,
            "status": "published",
            "attributes": {"compartment": "water"},
        },
        {
            "iri": MASS,
            "type": "unit-group",
            "pref_label": "Units of mass",
            "source": CORE,
            "status": "published",
        },
        {
            "iri": STEEL,
            "type": "process",
            "pref_label": "Steel",
            "source": CORE,
            "status": "published",
            "attributes": {
                "valid_from": "2020-01-01",
                "process_type": "unit",
                "technology": "BOF",
            },
        },
    ]


def core_relations():
    return [
        {
            "subject": FLOWS + "ENVO_00002010",
            "predicate": "skos:broader",
            "object": FLOWS + "ENVO_00002006",
            "source": CORE,
            "status": "published",
        },
        {
            "subject": FLOWS + "ENVO_00002006",
            "predicate": "skos:exactMatch",
            "object": "http://purl.obolibrary.org/obo/ENVO_00002006",
            "source": CORE,
            "status": "published",
        },
        {
            "subject": MASS,
            "predicate": "qudt:hasUnit",
            "object": KG,
            "source": CORE,
            "status": "published",
        },
        {
            "subject": STEEL,
            "predicate": "ont:geography",
            "object": "https://sws.geonames.org/6295630/",
            "source": CORE,
            "status": "published",
        },
    ]


def ef_terms():
    return [
        {"iri": EF, "type": "source", "pref_label": "EF 3.1", "source": EF, "status": "published"},
        {
            "iri": FLOWS + "0000b186",
            "type": "elementary-flow",
            "pref_label": "Isosorbide",
            "source": EF,
            "status": "draft",
            "attributes": {"compartment": "air", "cas_number": "64896-70-4"},
            "alt_labels": ["D-Glucitol"],
            "additional_notations": ["ec:807-840-4"],
        },
    ]


@pytest.fixture
def layout(tmp_path):
    terms = tmp_path / "terms"
    relations = tmp_path / "relations"
    write_terms(core_terms(), terms, "sentier-core")
    write_relations(core_relations(), relations, "sentier-core")
    write_terms(ef_terms(), terms, "ef-3.1")
    return terms, relations
