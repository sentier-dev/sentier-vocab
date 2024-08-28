from .graph_base import GraphBase
from rdflib import Graph, Literal, Namespace, URIRef
from pathlib import Path
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS
from .utils import get_one_in_graph

EF_ISO = "Material or energy entering the system being studied that has been drawn from the environment without previous human transformation, or material or energy leaving the system being studied that is released into the environment without subsequent human transformation."
OBO = Namespace("http://www.geneontology.org/formats/oboInOwl/")


LANGUAGE_AWARE = {SKOS.definition, SKOS.altLabel, SKOS.prefLabel}
VERB_MAPPING = {
    URIRef(
        "http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym"
    ): SKOS.altLabel,
    URIRef(
        "http://www.geneontology.org/formats/oboInOwl#hasExactSynonym"
    ): SKOS.altLabel,
    URIRef("http://www.geneontology.org/formats/oboInOwl#hasDbXref"): SKOS.related,
    URIRef("http://purl.obolibrary.org/obo/IAO_0000115"): SKOS.definition,
    RDFS.label: SKOS.prefLabel,
}


class ENVO(GraphBase):
    REPO_URL = "https://github.com/EnvironmentOntology/envo"
    BASE_URI = "https://vocab.sentier.dev/flows/envo/"

    def __init__(self):
        super().__init__()
        self.envo_graph = self.get_graph_for_file("/envo.owl")
        self.graph = Graph()
        self.CS = self.add_concept_scheme()
        self.add_water()

    def add_concept_scheme(self) -> URIRef:
        CS = URIRef("https://vocab.sentier.dev/flows/")
        self.add((CS, RDF.type, SKOS.ConceptScheme))
        self.add(
            (
                CS,
                SKOS.prefLabel,
                self.as_language_aware_literal("Elementary flows"),
            )
        )
        self.add(
            (
                CS,
                SKOS.altLabel,
                self.as_language_aware_literal("Biosphere flows"),
            )
        )
        self.add((CS, SKOS.definition, self.as_language_aware_literal(EF_ISO)))
        return CS

    def add_water(self) -> None:
        freshwater_envo = URIRef("http://purl.obolibrary.org/obo/ENVO_00002006")
        freshwater = URIRef(self.BASE_URI + "ENVO_00002006")

        self.add((freshwater, RDF.type, SKOS.Concept))
        self.add((freshwater, SKOS.inScheme, self.CS))
        self.add((freshwater, SKOS.exactMatch, freshwater_envo))

        for s, v, o in self.envo_graph.triples((freshwater_envo, None, None)):
            try:
                verb = VERB_MAPPING[v]
                self.add(
                    (
                        freshwater,
                        verb,
                        self.as_language_aware_literal(o)
                        if verb in LANGUAGE_AWARE
                        else o,
                    )
                )
            except KeyError:
                continue

        self.recurse_relationship(freshwater_envo, freshwater)

    def recurse_relationship(self, envo_uri: URIRef, sd_uri: URIRef) -> None:
        for child_uri, _, _ in self.envo_graph.triples(
            (None, RDFS.subClassOf, envo_uri)
        ):
            this_uri = URIRef(self.BASE_URI + self.get_identifier(child_uri))
            self.add((this_uri, RDF.type, SKOS.Concept))
            self.add((this_uri, SKOS.inScheme, self.CS))
            self.add((this_uri, SKOS.exactMatch, child_uri))
            self.add((this_uri, SKOS.broader, sd_uri))
            self.add((sd_uri, SKOS.narrower, this_uri))

            for _, v, o in self.envo_graph.triples((child_uri, None, None)):
                try:
                    verb = VERB_MAPPING[v]
                    self.add(
                        (
                            this_uri,
                            verb,
                            self.as_language_aware_literal(o)
                            if verb in LANGUAGE_AWARE
                            else o,
                        )
                    )
                except KeyError:
                    continue

            self.recurse_relationship(child_uri, this_uri)

    def write_graph(
        self, filepath: str = "envo-sentier-dev.ttl", dirpath: Path | None = None
    ) -> Path:
        if not filepath.endswith(".ttl"):
            filepath += ".ttl"
        if not dirpath:
            dirpath = Path.cwd()
        output_fp = Path(dirpath) / filepath
        self.graph.serialize(destination=output_fp)
        return output_fp


if __name__ == "__main__":
    ENVO().write_graph()
