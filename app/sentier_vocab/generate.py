"""Thin native-only pipeline: validate data/*.yaml -> emit output/*.ttl.

This does NOT merge importer output. Importers (app/sentier_vocab/importers/) are
independent and emit their own TTL separately.
"""

from pathlib import Path

from linkml_runtime import SchemaView
from rdflib import Graph
from rdflib import Namespace as RDFNamespace
from rdflib import URIRef
from rdflib.namespace import RDF, SKOS

from sentier_vocab.errors import SchemaValidationError
from sentier_vocab.iris import NAMESPACES
from sentier_vocab.loaders import load_source
from sentier_vocab.ordered_serialization import OrderedTurtleSerializer
from sentier_vocab.rdf_mapping import concept_to_triples, member_slot_and_class, schema_view
from sentier_vocab.schemas import validate_collection


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


def _check_registered_scheme(scheme: str, source: Path | str) -> None:
    if scheme not in set(NAMESPACES.values()):
        raise SchemaValidationError(
            f"{source}: scheme {scheme!r} is not a registered Sentier.dev namespace "
            f"(see sentier_vocab.iris.NAMESPACES)"
        )


def generate_sources(
    schema_path: Path | str,
    data_paths: list[Path | str],
    output_path: Path | str,
) -> Path:
    """Validate and merge one or more source files (YAML or Parquet) into one TTL.

    Every source for a category must declare the same registered ``scheme``; their
    records are concatenated into a single SKOS graph. Each source is validated against
    the schema via :func:`validate_collection` (format-agnostic). Returns the output path.
    """
    sv = schema_view(str(schema_path))
    collection_key, class_name = member_slot_and_class(sv)

    schemes: set[str] = set()
    records: list[dict] = []
    for data_path in data_paths:
        scheme, source_records = load_source(data_path, collection_key)
        _check_registered_scheme(scheme, data_path)
        validate_collection(scheme, source_records, collection_key, schema_path)
        schemes.add(scheme)
        records.extend(source_records)

    if len(schemes) > 1:
        raise SchemaValidationError(
            f"{output_path}: sources declare conflicting schemes {sorted(schemes)}; "
            f"all files in a category must share one ConceptScheme"
        )
    if not schemes:
        raise SchemaValidationError(f"{output_path}: no source files provided")

    graph = build_graph(records, schemes.pop(), sv, class_name)
    return write_ttl(graph, output_path)


def generate_category(
    category: str,
    schema_path: Path | str,
    data_path: Path | str,
    output_path: Path | str,
) -> Path:
    """Validate one data file, build its graph, and write the TTL. Returns the output path.

    Thin single-file wrapper over :func:`generate_sources`.
    """
    return generate_sources(schema_path, [data_path], output_path)
