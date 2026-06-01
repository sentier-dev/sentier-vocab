"""Thin native-only pipeline: validate data/*.yaml -> emit output/*.ttl.

This does NOT merge importer output. Importers (app/sentier_vocab/importers/) are
independent and emit their own TTL separately.
"""

from pathlib import Path

import yaml
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS

from sentier_vocab.errors import SchemaValidationError
from sentier_vocab.iris import NAMESPACES
from sentier_vocab.ordered_serialization import OrderedTurtleSerializer
from sentier_vocab.schemas import validate_data_file

DEFAULT_LANG = "en"

# Each category's collection file uses one top-level list key.
CATEGORY_COLLECTION_KEY = {
    "elementary-flows": "flows",
}


def _lang(value: str) -> Literal:
    return Literal(value, lang=DEFAULT_LANG)


def build_graph(concepts: list[dict], scheme_uri: str) -> Graph:
    """Build an rdflib SKOS graph from a list of concept dicts."""
    # Pilot scope: only the shared SKOS spine is serialized. Domain-specific slots
    # defined in the per-type LinkML schemas (e.g. compartment, sub_compartment,
    # cas_number, formula) are intentionally NOT emitted yet — they have no canonical
    # RDF predicate assigned, and `status` is internal curation metadata not published
    # to the vocabulary. Per-category serialization is follow-on work.
    graph = Graph()
    graph.bind("skos", SKOS)
    scheme = URIRef(scheme_uri)
    graph.add((scheme, RDF.type, SKOS.ConceptScheme))

    for concept in concepts:
        uri = URIRef(concept["iri"])
        graph.add((uri, RDF.type, SKOS.Concept))
        graph.add((uri, SKOS.inScheme, scheme))
        graph.add((uri, SKOS.prefLabel, _lang(concept["pref_label"])))
        if concept.get("definition"):
            graph.add((uri, SKOS.definition, _lang(concept["definition"])))
        for alt in concept.get("alt_labels") or []:
            graph.add((uri, SKOS.altLabel, _lang(alt)))
        if concept.get("notation"):
            graph.add((uri, SKOS.notation, Literal(concept["notation"])))
        if concept.get("broader"):
            graph.add((uri, SKOS.broader, URIRef(concept["broader"])))
        for match in concept.get("exact_match") or []:
            graph.add((uri, SKOS.exactMatch, URIRef(match)))
        for match in concept.get("close_match") or []:
            graph.add((uri, SKOS.closeMatch, URIRef(match)))
        for rel in concept.get("related") or []:
            graph.add((uri, SKOS.related, URIRef(rel)))

    return graph


def write_ttl(graph: Graph, output_path: Path | str) -> Path:
    """Serialize a graph to TTL using the stable, diff-friendly ordered serializer."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serializer = OrderedTurtleSerializer(graph)
    with open(output_path, "wb") as fp:
        serializer.serialize(fp)
    return output_path


def generate_category(
    category: str,
    schema_path: Path | str,
    data_path: Path | str,
    output_path: Path | str,
) -> Path:
    """Validate one data file, build its graph, and write the TTL. Returns the output path."""
    validate_data_file(data_path, schema_path)
    raw = yaml.safe_load(Path(data_path).read_text())
    scheme = raw["scheme"]
    if scheme not in set(NAMESPACES.values()):
        raise SchemaValidationError(
            f"{data_path}: scheme {scheme!r} is not a registered Sentier.dev namespace "
            f"(see sentier_vocab.iris.NAMESPACES)"
        )
    collection_key = CATEGORY_COLLECTION_KEY.get(category, "concepts")
    concepts = raw.get(collection_key) or []
    graph = build_graph(concepts, scheme)
    return write_ttl(graph, output_path)
