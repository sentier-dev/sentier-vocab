from pathlib import Path

import skosify
from loguru import logger
from rdflib import Graph

filepath = Path(__file__).parent / "input" / "model-terms.ttl"


def ModelTerms():
    logger.info("Reading input TTL file {}", filepath.absolute())
    graph = Graph().parse(filepath)
    logger.info("Creating reciprocal relations")
    skosify.infer.skos_topConcept(graph)
    skosify.infer.skos_hierarchical(graph, narrower=True)
    skosify.infer.skos_transitive(graph, narrower=True)

    output_path = Path(__file__).parent / "output" / "model-terms.reciprocal.ttl"
    logger.info("Writing output TTL file {}", output_path)
    graph.serialize(destination=output_path)
    return filepath.with_suffix(".ttl")


if __name__ == "__main__":
    ModelTerms()
