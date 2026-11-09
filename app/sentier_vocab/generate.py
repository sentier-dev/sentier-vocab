"""Emit SKOS TTL from the terms/ and relations/ layers.

One graph per (category, input file): ``output/<category>.ttl`` for the
``sentier-core`` release, ``output/<category>.<file-stem>.ttl`` for every other
file. A relation row is serialised into the graph of its subject's term.
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal
from rdflib import Namespace as RDFNamespace
from rdflib import URIRef
from rdflib.namespace import RDF, SKOS, XSD

from sentier_vocab import paths
from sentier_vocab.layers import load_relations, load_terms, release_of
from sentier_vocab.ordered_serialization import OrderedTurtleSerializer
from sentier_vocab.schema import (
    Attribute,
    RelationSchema,
    TermSchema,
    load_relation_schema,
    load_term_schema,
)

PRIMARY_RELEASE = "sentier-core"


def output_name(category: str, stem: str) -> str:
    """``flows.ttl`` for the sentier-core release, ``flows.<stem>.ttl`` otherwise."""
    if release_of(stem) == PRIMARY_RELEASE:
        return f"{category}.ttl"
    return f"{category}.{stem}.ttl"


def _attribute_node(value, spec: Attribute) -> Literal | URIRef:
    if spec.type == "uri":
        return URIRef(str(value))
    if spec.type == "date":
        return Literal(str(value), datatype=XSD.date)
    if spec.type == "double":
        return Literal(float(value))
    if spec.lang:
        return Literal(str(value), lang=spec.lang)
    return Literal(str(value))


def _column_node(column_name: str, value, lang: str | None) -> Literal | URIRef:
    if column_name == "source":
        return URIRef(value)
    if lang:
        return Literal(str(value), lang=lang)
    return Literal(str(value))


def term_triples(row: dict, schema: TermSchema) -> list[tuple]:
    """rdf:type, skos:inScheme, column triples and attribute triples of one term row."""
    term_type = schema.types[row["type"]]
    subject = URIRef(row["iri"])
    triples = [
        (subject, RDF.type, URIRef(term_type.class_uri)),
        (subject, SKOS.inScheme, URIRef(term_type.namespace)),
    ]
    for column in schema.columns.values():
        value = row.get(column.name)
        if column.predicate is None or value is None:
            continue
        for item in value if isinstance(value, list) else [value]:
            triples.append(
                (subject, URIRef(column.predicate), _column_node(column.name, item, column.lang))
            )
    for name, value in (row.get("attributes") or {}).items():
        spec = term_type.attributes[name]
        for item in value if isinstance(value, list) else [value]:
            triples.append((subject, URIRef(spec.predicate), _attribute_node(item, spec)))
    return triples


def relation_triple(row: dict, rel_schema: RelationSchema) -> tuple:
    """The one triple a relation row stands for."""
    predicate = rel_schema.predicates[row["predicate"]]
    return (URIRef(row["subject"]), URIRef(predicate.uri), URIRef(row["object"]))


def _new_graph(schema: TermSchema, rel_schema: RelationSchema) -> Graph:
    graph = Graph()
    for prefix, uri in {**schema.prefixes, **rel_schema.prefixes}.items():
        graph.bind(prefix, RDFNamespace(uri))
    return graph


def build_graphs(
    terms: dict[Path, list[dict]],
    relations: dict[Path, list[dict]],
    schema: TermSchema | None = None,
    rel_schema: RelationSchema | None = None,
) -> dict[tuple[str, str], Graph]:
    """``{(category, file stem): graph}`` for every type present in every term file."""
    schema = schema or load_term_schema(paths.TERM_SCHEMA)
    rel_schema = rel_schema or load_relation_schema(paths.RELATION_SCHEMA)
    graphs: dict[tuple[str, str], Graph] = {}
    location: dict[str, tuple[str, str]] = {}
    for path, rows in terms.items():
        for row in rows:
            term_type = schema.types[row["type"]]
            key = (term_type.category, path.stem)
            graph = graphs.get(key)
            if graph is None:
                graph = graphs[key] = _new_graph(schema, rel_schema)
                graph.add((URIRef(term_type.namespace), RDF.type, SKOS.ConceptScheme))
            for triple in term_triples(row, schema):
                graph.add(triple)
            location[row["iri"]] = key
    orphans = set()
    for rows in relations.values():
        for row in rows:
            key = location.get(row["subject"])
            if key is None:
                orphans.add(row["subject"])
                continue
            graphs[key].add(relation_triple(row, rel_schema))
    if orphans:
        raise ValueError(f"relations with unknown subjects: {sorted(orphans)[:5]}")
    return graphs


def write_ttl(graph: Graph, output_path: Path | str) -> Path:
    """Serialize a graph with the stable, diff-friendly ordered serializer."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as fp:
        OrderedTurtleSerializer(graph).serialize(fp)
    return output_path


def generate(
    terms_dir: Path | str = paths.TERMS_DIR,
    relations_dir: Path | str = paths.RELATIONS_DIR,
    output_dir: Path | str = paths.OUTPUT_DIR,
) -> list[Path]:
    """Build every graph and write it. Returns the files written, in name order."""
    relations = load_relations(relations_dir) if Path(relations_dir).exists() else {}
    graphs = build_graphs(load_terms(terms_dir), relations)
    written = [
        write_ttl(graph, Path(output_dir) / output_name(category, stem))
        for (category, stem), graph in sorted(graphs.items())
    ]
    return sorted(written)
