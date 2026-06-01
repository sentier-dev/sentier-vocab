import skosify
from loguru import logger
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

from sentier_vocab.graph_base import GraphBase
from sentier_vocab.utils import get_file_in_downloadable_zip_archive

OEO = Namespace("http://openenergy-platform.org/ontology/oeo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")

MATCHES = {
    # Hydrogen
    URIRef(OEO + "OEO_00000220"): URIRef("http://data.europa.eu/xsp/cn2024/280410000080"),
    # Electrical energy
    URIRef(OEO + "OEO_00000139"): URIRef("http://data.europa.eu/xsp/cn2024/271600000080"),
}
NARROWER = {
    ### Hydrogen
    # Fossil hydrogen
    URIRef(OEO + "OEO_00010015"): URIRef("http://data.europa.eu/xsp/cn2024/280410000080"),
    # Synthetic hydrogen
    URIRef(OEO + "OEO_00010016"): URIRef("http://data.europa.eu/xsp/cn2024/280410000080"),
    # Electrolytic hydrogen
    URIRef(OEO + "OEO_00010379"): URIRef("http://data.europa.eu/xsp/cn2024/280410000080"),
    # Renewable electrolytic hydrogen
    URIRef(OEO + "OEO_00010380"): URIRef(OEO + "OEO_00010379"),
    # Nuclear electrolytic hydrogen
    URIRef(OEO + "OEO_00010416"): URIRef(OEO + "OEO_00010379"),
    # Solar electrolytic hydrogen
    URIRef(OEO + "OEO_00010418"): URIRef(OEO + "OEO_00010379"),
    # Steam reforming hydrogen
    URIRef(OEO + "OEO_00010381"): URIRef("http://data.europa.eu/xsp/cn2024/280410000080"),
    # Fossil steam reforming hydrogen
    URIRef(OEO + "OEO_00010382"): URIRef(OEO + "OEO_00010381"),
    # Fossil steam reforming hydrogen with CCS
    URIRef(OEO + "OEO_00010383"): URIRef(OEO + "OEO_00010381"),
    ### Electricity
    # renewable electrical energy
    URIRef(OEO + "OEO_00010384"): URIRef("http://data.europa.eu/xsp/cn2024/271600000080"),
    # nuclear electrical energy
    URIRef(OEO + "OEO_00010417"): URIRef("http://data.europa.eu/xsp/cn2024/271600000080"),
    # solar electrical energy
    URIRef(OEO + "OEO_00010419"): URIRef("http://data.europa.eu/xsp/cn2024/271600000080"),
}

MAPPING = {
    URIRef(OBO + "IAO_0006011"): SKOS.closeMatch,
    URIRef(OBO + "IAO_0000118"): SKOS.altLabel,
    URIRef(OBO + "IAO_0000115"): SKOS.definition,
    URIRef(OBO + "IAO_0000119"): SKOS.related,
    RDFS.label: SKOS.prefLabel,
}


class OpenEnergyProducts(GraphBase):
    def __init__(self, graph: Graph | None = None):
        logger.info("Parsing and creating Open Energy Ontology elements")
        data = get_file_in_downloadable_zip_archive(
            "https://openenergyplatform.org/ontology/oeo/releases/latest", "oeo-full.owl"
        )
        self.input_graph = Graph().parse(data, format="xml")
        new_graph = graph is None
        self.graph = graph or Graph()

        for key, value in MATCHES.items():
            self.graph.add((key, SKOS.exactMatch, value))
            self.graph.add((key, RDF.type, SKOS.Concept))

        for key, value in NARROWER.items():
            self.graph.add((key, SKOS.broader, value))
            self.graph.add((key, RDF.type, SKOS.Concept))

            for _, p, o in self.input_graph.triples((key, None, None)):
                try:
                    self.graph.add((key, MAPPING[p], o))
                except KeyError:
                    continue
        if new_graph:
            skosify.infer.skos_topConcept(self.graph)
            skosify.infer.skos_hierarchical(self.graph, narrower=True)
            skosify.infer.skos_transitive(self.graph, narrower=True)


if __name__ == "__main__":
    OpenEnergyProducts().write_graph("oeo-product-vocab.ttl")
