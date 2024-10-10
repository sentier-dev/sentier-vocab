from pathlib import Path

import skosify
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS

from .ordered_serialization import OrderedTurtleSerializer

VAEM = Namespace("http://www.linkedmodel.org/schema/vaem")
QUDTS = Namespace("http://qudt.org/schema/qudt/")
QUDTV = Namespace("http://qudt.org/vocab/")
QK = QUDTV.quantitykind


COMMON_PREDICATES = {
    "broader": SKOS.broader,
    "narrower": SKOS.narrower,
    "prefLabel": SKOS.prefLabel,
    "altLabel": SKOS.altLabel,
    "hiddenLabel": SKOS.hiddenLabel,
    "notation": SKOS.notation,
    "definition": SKOS.definition,
    "related": SKOS.related,
    "exactMatch": SKOS.exactMatch,
    "closeMatch": SKOS.closeMatch,
    "inScheme": SKOS.inScheme,
    "isDefinedBy": RDFS.isDefinedBy,
    "isReplacedBy": DCTERMS.isReplacedBy,
    "type": RDF.type,
    "hasQuantityKind": QUDTS.hasQuantityKind,
    "hasDimensionVector": QUDTS.hasDimensionVector,
    "conversionMultiplier": QUDTS.conversionMultiplier,
    "conversionMultiplier": QUDTS.conversionMultiplier,
    "conversionMultiplierSN": QUDTS.conversionMultiplierSN,
}
OBJECT_TYPES_FOR_PREDICATES = {
    SKOS.broader: Literal,
    SKOS.narrower: Literal,
    SKOS.prefLabel: Literal,
    SKOS.altLabel: Literal,
    SKOS.hiddenLabel: Literal,
    SKOS.notation: Literal,
    SKOS.definition: Literal,
    SKOS.related: URIRef,
    SKOS.exactMatch: URIRef,
    SKOS.closeMatch: URIRef,
    SKOS.inScheme: URIRef,
    RDFS.isDefinedBy: URIRef,
    DCTERMS.isReplacedBy: URIRef,
    RDF.type: URIRef,
    QUDTS.hasQuantityKind: URIRef,
    QUDTS.hasDimensionVector: URIRef,
    QUDTS.conversionMultiplier: URIRef,
    QUDTS.conversionMultiplier: URIRef,
    QUDTS.conversionMultiplierSN: URIRef,
}
COMMON_OBJECTS = {
    "Concept": SKOS.Concept,
    "ConceptScheme": SKOS.ConceptScheme,
}


def add_custom_terms(data: list[dict], namespace: str, filename: str) -> Path:
    """Add new `Concept` terms, validate them, and serialize the graph.

    `data` is a list of dicts which define each triple. The dicts can have the following structure:

    ```python
    {
        'subject': str, # required; will be combined with `namespace` and turned into a `URIRef`
        'predicate': str | URIRef, # required; see COMMON_PREDICATES for allowed strings
        'object': str | URIRef | Literal, # required; type will be inferred from predicate if possible
        'language': str  # optional; only for literal `object` values.
    }
    ```

    If given a string, and the `predicate` is `RDF.type`, `object` will use `COMMON_OBJECTS` mapping if possible.

    """
    if not namespace or not isinstance(namespace, str):
        raise ValueError("namespace must be a string")
    if not filename or not isinstance(filename, str):
        raise ValueError("filename must be a string")

    graph = Graph()
    for line in data:
        if len(line) == 3:
            s, p, o = line
            lang = None
        elif len(line) == 4:
            s, p, o, lang = line
        else:
            raise ValueError(f"Data line {line} has wrong number of elements")

        object_type = None
        subject = URIRef(namespace + s)

        if isinstance(p, URIRef):
            predicate = p
        elif isinstance(p, str):
            try:
                predicate = COMMON_PREDICATES[p]
            except KeyError:
                raise KeyError(f"Predicate {p} not in common predicates; pass a `URIRef` instead")
        else:
            raise ValueError(f"Predicate {p} has incorrect type for this function")

        try:
            object_type = OBJECT_TYPES_FOR_PREDICATES[predicate]
        except KeyError:
            pass

        if isinstance(o, (Literal, URIRef)):
            object_ = o
        elif predicate is RDF.type and o in COMMON_OBJECTS:
            object_ = COMMON_OBJECTS[o]
        elif object_type is not None:
            if object_type is Literal:
                if lang is not None:
                    object_ = Literal(o, lang=lang)
                else:
                    object_ = Literal(o)
            else:
                object_ = URIRef(o)
        else:
            raise ValueError(f"Object {o} can be translated into correct form")

        if object_type is not None and not isinstance(object_, object_type):
            raise ValueError(
                f"Object {object_} has incorrect type for this function; should be {type(object_type)} but got {type(object_)}"
            )

        graph.add((subject, predicate, object_))

    skosify.infer.skos_topConcept(graph)
    skosify.infer.skos_hierarchical(graph, narrower=True)
    skosify.infer.skos_transitive(graph, narrower=True)

    output_path = (Path(__file__).parent / "output" / filename).with_suffix(".ttl")
    serializer = OrderedTurtleSerializer(graph)
    with open(output_path, "wb") as fp:
        serializer.serialize(fp)

    return output_path
