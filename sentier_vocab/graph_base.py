from pathlib import Path

import skosify
from rdflib import Graph, Literal, Namespace, URIRef

from sentier_vocab.utils import DEFAULT_DATA_DIR, GithubZipfileRelease


class GraphBase:
    def __init__(
        self,
        *args,
        data_dir: Path = DEFAULT_DATA_DIR,
        default_lang: str = "en",
        **kwargs,
    ) -> None:
        self.default_lang = default_lang
        self.zip_archive = GithubZipfileRelease(repo_url=self.REPO_URL, data_dir=data_dir)

    def as_language_aware_literal(self, obj: Literal | str, en_title: bool = False) -> Literal:
        if isinstance(obj, str):
            obj = Literal(obj)
        if not obj.language:
            if en_title and self.default_lang.lower().startswith("en"):
                return Literal(str(obj).title(), lang=self.default_lang)
            else:
                return Literal(obj, lang=self.default_lang)
        else:
            if en_title and obj.language.lower().startswith("en"):
                return Literal(str(obj).title(), lang=obj.language)
            else:
                return obj

    def get_graph_for_file(self, filepath: str) -> Graph:
        if filepath.lower().endswith("xml") or filepath.lower().endswith("owl"):
            return Graph().parse(self.zip_archive.get_file_in_archive(filepath), format="xml")
        else:
            return Graph().parse(self.zip_archive.get_file_in_archive(filepath))

    def add(self, triple: tuple) -> None:
        # Convenient place to put logging or debug checks
        self.graph.add(triple)

    def skosify_checks(self):
        # Can't use - create backwards related links to nodes not defined in our graph
        # skosify.infer.skos_related(self.graph)
        skosify.infer.skos_topConcept(self.graph)
        skosify.infer.skos_hierarchical(self.graph, narrower=True)
        skosify.infer.skos_transitive(self.graph, narrower=True)
        # skosify.infer.rdfs_classes(self.graph)
        # skosify.infer.rdfs_properties(self.graph)

    def get_identifier(self, uri: URIRef) -> str:
        return uri.split("/")[-1]
