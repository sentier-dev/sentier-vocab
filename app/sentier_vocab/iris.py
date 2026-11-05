"""Central registry of published Sentier.dev IRI namespaces.

The namespaces are read from ``schemas/term.yaml`` (the ``types`` section): that
file is the stability contract for the published vocabulary. ``NAMESPACES`` keeps
its historical shape, ``{category: namespace}``, so external code keeps working.
"""

import types
from typing import Mapping

from rdflib import Namespace, URIRef

from sentier_vocab import paths
from sentier_vocab.schema import load_term_schema

__all__ = (
    "NAMESPACES",
    "ONTOLOGY",
    "namespace_for",
    "iri_for",
    "iri_for_cf",
    "identifier_from",
    "category_for_type",
    "type_for_iri",
)

BASE = "https://vocab.sentier.dev/"
ONTOLOGY = BASE + "ontology/"

_SCHEMA = load_term_schema(paths.TERM_SCHEMA)

NAMESPACES: Mapping[str, str] = types.MappingProxyType(
    {t.category: t.namespace for t in _SCHEMA.types.values()}
)

# Longest namespace first so units/group/ wins over units/.
_TYPES_BY_NAMESPACE = sorted(
    ((t.namespace, t.name) for t in _SCHEMA.types.values()),
    key=lambda pair: -len(pair[0]),
)


def namespace_for(category: str) -> Namespace:
    """Return the rdflib Namespace for a category key. Raises KeyError if unknown."""
    return Namespace(NAMESPACES[category])


def iri_for(category: str, identifier: str) -> URIRef:
    """Build the full IRI for a term in a category."""
    return namespace_for(category)[identifier]


def iri_for_cf(method_id: str, impact_id: str, flow_id: str) -> URIRef:
    """Deterministic IRI for a characterization factor (method + impact category + flow).

    Kept so sentier-methods can mint the same IRIs; vocab stores no CF rows.
    """
    return namespace_for("characterization-factors")[f"{method_id}_{impact_id}_{flow_id}"]


def identifier_from(iri: str | URIRef) -> str:
    """Trailing identifier of a full term IRI (not a bare namespace)."""
    return str(iri).rstrip("/").split("/")[-1]


def category_for_type(type_name: str) -> str:
    """The output/iris category of a term type (``elementary-flow`` -> ``flows``)."""
    return _SCHEMA.types[type_name].category


def type_for_iri(iri: str) -> str | None:
    """The term type whose namespace is the longest prefix of ``iri``, or None."""
    for namespace, type_name in _TYPES_BY_NAMESPACE:
        if iri.startswith(namespace):
            return type_name
    return None
