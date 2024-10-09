import argparse
import re
from pathlib import Path

import skosify
from loguru import logger
from rdflib import Graph, Literal

from sentier_vocab.open_energy_ontology import OpenEnergyProducts

sanity = re.compile("^[0-9 ]*[-]+ ")
# sanity.match("0102 29 41 ----- For slaughter")
# re.sub(sanity, "", "0102 29 41 ----- For slaughter")


def CN2024(filepath: Path):
    logger.info("Reading input RDF file {}", filepath.absolute())
    graph = Graph().parse(filepath)

    logger.info("Changing labels to remove notation")
    for s, v, o in graph.triples((None, None, None)):
        if isinstance(o, Literal) and isinstance(o.value, str) and sanity.match(o.value):
            graph.add((s, v, Literal(re.sub(sanity, "", o.value).strip(), lang=o.language)))
            graph.remove((s, v, o))

    OpenEnergyProducts(graph)

    logger.info("Creating reciprocal relations")
    skosify.infer.skos_topConcept(graph)
    skosify.infer.skos_hierarchical(graph, narrower=True)
    skosify.infer.skos_transitive(graph, narrower=True)

    output_path = filepath.with_suffix(".ttl")
    logger.info("Writing output TTL file {}", output_path)
    graph.serialize(destination=output_path)
    return filepath.with_suffix(".ttl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="CN2024 conversion utility",
        description="Take the `CN 2024 (RDF dataset)` file from `https://showvoc.op.europa.eu/#/datasets/ESTAT_Combined_Nomenclature,_2024_%28CN_2024%29/metadata` and process it.",
    )
    parser.add_argument("filepath")
    args = parser.parse_args()
    CN2024(Path(args.filepath))
