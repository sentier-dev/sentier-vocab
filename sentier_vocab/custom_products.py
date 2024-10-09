from rdflib import Graph, Namespace, URIRef
from sentier_vocab.graph_base import GraphBase
from sentier_vocab.data.input.custom_products import CUSTOM_PRODUCTS_DATA
from rdflib.namespace import RDFS, SKOS, RDF
import skosify
from loguru import logger

PRODUCTS = Namespace("http://vocab.sentier.dev/products")


class CustomProducts(GraphBase):
    def __init__(self):
        self.graph = Graph()
        for triple in CUSTOM_PRODUCTS_DATA:
            self.graph.add(triple)

        skosify.infer.skos_topConcept(self.graph)
        skosify.infer.skos_hierarchical(self.graph, narrower=True)
        skosify.infer.skos_transitive(self.graph, narrower=True)


if __name__ == "__main__":
    fp = CustomProducts().write_graph("custom-products.ttl")
    logger.info(f"Created custom graph at {fp}")
