from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, SKOS
import re
from pathlib import Path
from io import BytesIO


sanity = re.compile("^[0-9 ]*[-]+ ")
# sanity.match("0102 29 41 ----- For slaughter")
# re.sub(sanity, "", "0102 29 41 ----- For slaughter")


CS_TO_DROP = {
    DCTERMS.language,
    SKOS.hasTopConcept,
}
CS_MAPPING = {
    DCTERMS.description: SKOS.definition,
}


class CombinedNomenclature:
    def __init__(self, filepath: Path, year: int):
        # logger.info("Reading input RDF file {}", filepath.absolute())
        self.graph = Graph().parse(filepath)
        self.year = year

    def concept_scheme(self) -> Graph:
        graph = Graph()
        cs_uri = URIRef(f"http://data.europa.eu/xsp/cn20{self.year}/cn20{self.year}")

        for subj, verb, obj in self.graph.triples((cs_uri, None, None)):
            if verb in CS_TO_DROP:
                continue
            elif verb in CS_MAPPING:
                graph.add((subj, CS_MAPPING[verb], obj))
            else:
                graph.add((subj, verb, obj))

        graph.add((
            cs_uri,
            URIRef("http://purl.org/ontology/bibo/status"),
            URIRef("http://purl.org/ontology/bibo/status/accepted")
        ))

        return graph

    def expanded_json_ld_graph(self, graph: Graph) -> str:
        out = BytesIO()
        graph.serialize(out, format="json-ld", endocing="utf-8")
        out.seek(0)
        return out.read().decode("utf-8")
