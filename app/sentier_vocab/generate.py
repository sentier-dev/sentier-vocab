"""Thin native-only pipeline: validate data/*.yaml -> emit output/*.ttl.

This does NOT merge importer output. Importers (app/sentier_vocab/importers/) are
independent and emit their own TTL separately.
"""

from pathlib import Path

import yaml
from linkml_runtime import SchemaView
from rdflib import Graph
from rdflib import Namespace as RDFNamespace
from rdflib import URIRef
from rdflib.namespace import RDF, SKOS

from sentier_vocab.errors import SchemaValidationError
from sentier_vocab.iris import NAMESPACES
from sentier_vocab.ordered_serialization import OrderedTurtleSerializer
from sentier_vocab.rdf_mapping import concept_to_triples, member_slot_and_class, schema_view
from sentier_vocab.schemas import validate_data_file


def build_graph(concepts: list[dict], scheme_uri: str, sv: SchemaView, class_name: str) -> Graph:
    """Build an rdflib SKOS graph from a list of concept dicts using the schema engine."""
    graph = Graph()
    graph.bind("skos", SKOS)
    # Bind all schema-declared prefixes so rdflib never auto-assigns ns1/ns2,
    # which would make serialization non-deterministic.
    for prefix, uri in sv.schema.prefixes.items():
        graph.bind(prefix, RDFNamespace(str(uri.prefix_reference)))
    graph.add((URIRef(scheme_uri), RDF.type, SKOS.ConceptScheme))
    for record in concepts:
        for triple in concept_to_triples(record, class_name, sv, scheme_uri):
            graph.add(triple)
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
    sv = schema_view(str(schema_path))
    collection_key, class_name = member_slot_and_class(sv)
    concepts = raw.get(collection_key) or []
    graph = build_graph(concepts, scheme, sv, class_name)
    return write_ttl(graph, output_path)
