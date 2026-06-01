"""Central registry of published Sentier.dev IRI namespaces.

This module is the single source of truth for every `https://vocab.sentier.dev/`
namespace and the stability contract for the published vocabulary. All term
generation and schema prefixes reference it; nothing should hardcode these
strings elsewhere.
"""

import types
from typing import Mapping

from rdflib import Namespace, URIRef

__all__ = ("NAMESPACES", "ONTOLOGY", "namespace_for", "iri_for", "iri_for_cf", "identifier_from")

BASE = "https://vocab.sentier.dev/"
ONTOLOGY = BASE + "ontology/"

NAMESPACES: Mapping[str, str] = types.MappingProxyType(
    {
        # Existing published namespaces — DO NOT change without a vocabulary migration.
        "flows": BASE + "flows/",
        "units": BASE + "units/",
        "products": BASE + "products/",
        "model-terms": BASE + "model-terms/",
        # New LCIA data types (ILCD-aligned).
        "flow-properties": BASE + "flow-properties/",
        "processes": BASE + "processes/",
        "lcia-methods": BASE + "lcia-methods/",
        "impact-categories": BASE + "impact-categories/",
        "characterization-factors": BASE + "characterization-factors/",
        "sources": BASE + "sources/",
        "contacts": BASE + "contacts/",
        # New term namespaces.
        "unit-groups": BASE + "units/group/",
    }
)


def namespace_for(category: str) -> Namespace:
    """Return the rdflib Namespace for a category key. Raises KeyError if unknown."""
    return Namespace(NAMESPACES[category])


def iri_for(category: str, identifier: str) -> URIRef:
    """Build the full IRI for a term in a category."""
    return namespace_for(category)[identifier]


def iri_for_cf(method_id: str, impact_id: str, flow_id: str) -> URIRef:
    """Deterministic IRI for a characterization factor (method + impact category + flow)."""
    return namespace_for("characterization-factors")[f"{method_id}_{impact_id}_{flow_id}"]


def identifier_from(iri: str | URIRef) -> str:
    """Extract the trailing identifier from a Sentier.dev term IRI.

    The *iri* argument must be a full **term** IRI — that is, a namespace IRI
    with an identifier appended, e.g.
    ``https://vocab.sentier.dev/flows/ENVO_00002006``.  Passing a bare
    namespace IRI (one that ends with ``/``) is undefined behaviour.
    """
    return str(iri).rstrip("/").split("/")[-1]
