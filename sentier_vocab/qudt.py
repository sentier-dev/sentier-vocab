import json
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

import requests
import skosify
from loguru import logger
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS

from sentier_vocab.errors import GraphFilterError, MissingDimensionVector
from sentier_vocab.utils import DEFAULT_DATA_DIR, get_one_in_graph, streaming_download

VAEM = Namespace("http://www.linkedmodel.org/schema/vaem")
# TODO: Get version through file inspection
QUDTS = Namespace("http://qudt.org/schema/qudt/")
QUDTV = Namespace("http://qudt.org/vocab/")
QK = QUDTV.quantitykind


vocab_data_dir = Path(__file__).parent / "data"
selected_fp = vocab_data_dir / "selected-quantity-kinds.json"
extra_concepts_data = vocab_data_dir / "extra-data.ttl"


class QUDT:
    def __init__(self, data_dir: Path = DEFAULT_DATA_DIR, default_lang: str = "en"):
        self.default_lang = default_lang
        self.selected_qk = {URIRef(k): v for k, v in json.load(open(selected_fp)).items()}
        self.zipped = ZipFile(open(self.get_latest_version(data_dir), "rb"))
        self.graph = Graph()
        self.zipfile_prefix = self.get_zipfile_prefix()
        concept_scheme = self.add_concept_scheme()
        mapping = self.add_quantity_kinds(concept_scheme)
        self.add_units(concept_scheme, mapping)
        self.graph.parse(extra_concepts_data)
        self.fill_missing_attributes()
        self.skosify_checks()

    def add(self, triple: tuple) -> None:
        # Convenient place to put logging or debug checks
        self.graph.add(triple)

    def get_latest_version(self, data_dir: Path) -> Path:
        try:
            catalogue = json.load(open(data_dir / "qudt.json"))
        except (OSError,):
            catalogue = {}
        release = requests.get(
            "https://api.github.com/repos/qudt/qudt-public-repo/releases/latest"
        ).json()["zipball_url"]
        if catalogue.get("release") != release:
            fp = str(streaming_download(release))
            with open("qudt.json", "w") as f:
                json.dump({"release": release, "filepath": fp}, f, indent=2)
            return fp
        return catalogue["filepath"]

    def get_zipfile_prefix(self) -> str:
        prefix = set()

        for zipinfo in self.zipped.infolist():
            prefix.add(zipinfo.filename.split("/")[0])

        assert len(prefix) == 1
        return prefix.pop()

    def get_graph_for_file(self, path: str) -> Graph:
        for zipinfo in self.zipped.infolist():
            if zipinfo.filename.startswith(self.zipfile_prefix + path):
                return Graph().parse(self.zipped.open(zipinfo.filename))
        raise KeyError

    def write_graph(
        self, filename: str = "qudt-sentier-dev.ttl", dirpath: Path | None = None
    ) -> Path:
        if not filename.endswith(".ttl"):
            filename += ".ttl"
        if not dirpath:
            dirpath = vocab_data_dir
        output_fp = Path(dirpath) / filename
        self.graph.serialize(destination=output_fp)
        return output_fp

    def skosify_checks(self):
        # Can't use - create backwards related links to nodes not defined in our graph
        # skosify.infer.skos_related(self.graph)
        skosify.infer.skos_topConcept(self.graph)
        skosify.infer.skos_hierarchical(self.graph, narrower=True)
        skosify.infer.skos_transitive(self.graph, narrower=True)
        # skosify.infer.rdfs_classes(self.graph)
        # skosify.infer.rdfs_properties(self.graph)

    def add_concept_scheme(self) -> URIRef:
        schema_graph = self.get_graph_for_file("/schema/SCHEMA_QUDT-v")
        ontology = get_one_in_graph(schema_graph, ((None, RDF.type, OWL.Ontology)))[0]
        graph_metdata_node = get_one_in_graph(
            schema_graph, (ontology, VAEM["#hasGraphMetadata"], None)
        )[2]

        CS = URIRef("https://vocab.sentier.dev/units/")
        self.add((CS, RDF.type, SKOS.ConceptScheme))
        self.add(
            (
                CS,
                SKOS.prefLabel,
                self.as_language_aware_literal(
                    get_one_in_graph(schema_graph, (ontology, RDFS.label, None))[2]
                ),
            )
        )

        for s, p, o in schema_graph.triples((graph_metdata_node, None, None)):
            if p.startswith(DCTERMS) and p not in [DCTERMS.title]:
                self.add((CS, p, o))

        return CS

    def as_language_aware_literal(self, obj: Literal, en_title: bool = False) -> Literal:
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

    def get_identifier(self, uri: URIRef) -> str:
        return uri.split("/")[-1]

    def deprecated(self, graph: Graph, key: URIRef) -> bool:
        return any(graph.triples((key, DCTERMS.isReplacedBy, None)))

    def check_that_deprecated_have_replaced_by(self, graph: Graph, kind: str) -> bool:
        # Note that it doesn't work the other way...
        replaced = {
            s for s, p, o in graph.triples((None, DCTERMS.isReplacedBy, None)) if s.startswith(kind)
        }
        deprecated = {
            s for s, p, o in graph.triples((None, QUDTS.deprecated, None)) if s.startswith(kind)
        }
        return deprecated.difference(replaced)

    def add_quantity_kinds(self, cs: URIRef) -> dict[URIRef, URIRef]:
        qk_graph = self.get_graph_for_file("/vocab/quantitykinds/VOCAB_QUDT-QUANTITY-KINDS-ALL-v")
        assert not self.check_that_deprecated_have_replaced_by(qk_graph, QK)

        qk_mapping = {
            s: URIRef("https://vocab.sentier.dev/units/quantity-kind/" + self.get_identifier(s))
            for s, p, o in qk_graph
            if URIRef(s) in self.selected_qk
            and s.startswith(QK)
            and not any(qk_graph.triples((s, DCTERMS.isReplacedBy, None)))
        }

        for key_uri, value_uri in qk_mapping.items():
            self.add((value_uri, RDF.type, SKOS.Concept))
            self.add((value_uri, SKOS.inScheme, cs))
            self.add((value_uri, SKOS.exactMatch, key_uri))
            self.add(
                (
                    value_uri,
                    QUDTS.hasDimensionVector,
                    get_one_in_graph(qk_graph, (key_uri, QUDTS.hasDimensionVector, None))[2],
                )
            )
            for s, v, o in qk_graph.triples((key_uri, SKOS.broader, None)):
                if o in self.selected_qk:
                    self.add((qk_mapping[s], SKOS.broader, qk_mapping[o]))
                    self.add((qk_mapping[o], SKOS.narrower, qk_mapping[s]))
            for s, v, o in qk_graph.triples((key_uri, RDFS.label, None)):
                self.add(
                    (
                        value_uri,
                        SKOS.prefLabel,
                        self.as_language_aware_literal(o, en_title=True),
                    )
                )

            verb_mapping = {
                DCTERMS.description: SKOS.definition,
                QUDTS.symbol: SKOS.altLabel,
                QUDTS.dbpediaMatch: SKOS.related,
                QUDTS.iec61360Code: SKOS.altLabel,
                QUDTS.informativeReference: QUDTS.informativeReference,
                QUDTS.isoNormativeReference: QUDTS.isoNormativeReference,
                QUDTS.latexDefinition: QUDTS.latexDefinition,
                QUDTS.latexSymbol: QUDTS.latexSymbol,
                QUDTS.siExactMatch: SKOS.exactMatch,
                RDFS.comment: SKOS.note,
                QUDTS.plainTextDescription: SKOS.note,
                RDFS.seeAlso: SKOS.related,
            }

            for s, v, o in qk_graph.triples((key_uri, None, None)):
                try:
                    self.add((value_uri, verb_mapping[v], o))
                except KeyError:
                    pass

        return qk_mapping

    def check_all_units_have_vector(self, graph: Graph) -> None:
        all_units = {s for s, p, o in graph.triples((None, None, None)) if s.startswith(QUDTV.unit)}
        with_dimension_vector = {
            s
            for s, p, o in graph.triples((None, QUDTS.hasDimensionVector, None))
            if s.startswith(QUDTV.unit)
        }
        if all_units.difference(with_dimension_vector):
            raise MissingDimensionVector

    @lru_cache(maxsize=1024)
    def is_unitary(self, graph: Graph, uri: URIRef) -> bool:
        try:
            return (
                float(get_one_in_graph(graph, ((uri, QUDTS.conversionMultiplier, None)))[2]) == 1.0
            )
        except GraphFilterError:
            logger.trace("No conversion multiplier for {u}", u=uri)
            return False

    def fill_missing_attributes(self) -> None:
        """Our custom concepts can be narrower than an existing QUDT unit. In these cases, we don't
        copy over all the additional data from the "parent" concept, but add it automatically."""
        all_units = {
            s
            for s, _, _ in self.graph.triples((None, RDF.type, SKOS.Concept))
            if s.startswith("https://vocab.sentier.dev/units/unit")
        }
        qk_mapping = {
            s: o
            for s, _, o in self.graph.triples((None, QUDTS.hasQuantityKind, None))
            if s in all_units
        }
        for uri in all_units.difference(set(qk_mapping)):
            possibles = [
                o
                for s, v, o in self.graph.triples((uri, SKOS.broader, None))
                if o.startswith("https://vocab.sentier.dev/units/unit")
            ]
            if not len(possibles) == 1:
                raise ValueError(f"Can't find broader match for concept {uri}")
            self.add((uri, QUDTS.hasQuantityKind, qk_mapping[possibles[0]]))

    def add_units(self, cs: URIRef, qk_mapping: dict[URIRef, URIRef]) -> None:
        unit_graph = self.get_graph_for_file("/vocab/unit/VOCAB_QUDT-UNITS-ALL-v")
        self.check_all_units_have_vector(unit_graph)

        unit_mapping = {
            s: URIRef("https://vocab.sentier.dev/units/unit" + str(s).replace(QUDTV.unit, ""))
            for s, p, o in unit_graph.triples((None, QUDTS.hasQuantityKind, None))
            if o in self.selected_qk and not any(unit_graph.triples((s, QUDTS.deprecated, None)))
        }

        # This is just terrible O(nonsense) code...
        top_level = {
            key: uri_v
            for key, value in self.selected_qk.items()
            for uri_k, uri_v in unit_mapping.items()
            if self.get_identifier(uri_k) == value
        }

        for key_uri, value_uri in unit_mapping.items():
            self.add_unit(uri=value_uri, unit_graph=unit_graph, cs=cs, qudt_uri=key_uri)

            for _, _, quantity_kind in unit_graph.triples((key_uri, QUDTS.hasQuantityKind, None)):
                if quantity_kind not in top_level:
                    continue
                if top_level[quantity_kind] == value_uri:
                    self.add((value_uri, SKOS.broader, qk_mapping[quantity_kind]))
                    self.add((value_uri, QUDTS.hasQuantityKind, qk_mapping[quantity_kind]))
                    self.add((qk_mapping[quantity_kind], SKOS.narrower, value_uri))
                else:
                    self.add((value_uri, SKOS.broader, top_level[quantity_kind]))
                    self.add((value_uri, QUDTS.hasQuantityKind, qk_mapping[quantity_kind]))
                    self.add((top_level[quantity_kind], SKOS.narrower, value_uri))

    def add_unit(self, uri: URIRef, unit_graph: Graph, cs: URIRef, qudt_uri: URIRef) -> None:
        self.add((uri, RDF.type, SKOS.Concept))
        self.add((uri, SKOS.inScheme, cs))
        self.add((uri, SKOS.exactMatch, qudt_uri))
        self.add(
            (
                uri,
                QUDTS.hasDimensionVector,
                get_one_in_graph(unit_graph, (qudt_uri, QUDTS.hasDimensionVector, None))[2],
            )
        )

        for s, v, o in unit_graph.triples((qudt_uri, RDFS.label, None)):
            self.add((uri, SKOS.prefLabel, self.as_language_aware_literal(o)))

        verb_mapping = {
            DCTERMS.description: SKOS.definition,
            QUDTS.plainTextDescription: SKOS.note,
            QUDTS.conversionMultiplier: QUDTS.conversionMultiplier,
            QUDTS.conversionMultiplierSN: QUDTS.conversionMultiplierSN,
            QUDTS.symbol: SKOS.notation,
            QUDTS.dbpediaMatch: SKOS.related,
            QUDTS.iec61360Code: SKOS.notation,
            QUDTS.uneceCommonCode: SKOS.notation,
            QUDTS.ucumCode: SKOS.notation,
            QUDTS.uneceCommonCode: SKOS.notation,
            QUDTS.informativeReference: QUDTS.informativeReference,
            QUDTS.isoNormativeReference: QUDTS.isoNormativeReference,
            QUDTS.latexDefinition: QUDTS.latexDefinition,
            QUDTS.latexSymbol: QUDTS.latexSymbol,
            QUDTS.siExactMatch: SKOS.exactMatch,
            RDFS.comment: SKOS.note,
            QUDTS.plainTextDescription: SKOS.note,
            RDFS.seeAlso: SKOS.related,
            QUDTS.applicableSystem: QUDTS.applicableSystem,
        }
        own_type = {
            QUDTS.symbol,
            QUDTS.iec61360Code,
            QUDTS.uneceCommonCode,
            QUDTS.ucumCode,
            QUDTS.uneceCommonCode,
        }

        for s, v, o in unit_graph.triples((qudt_uri, None, None)):
            try:
                verb = verb_mapping[v]
                if v in own_type:
                    self.add((uri, verb, Literal(o, datatype=v)))
                else:
                    self.add((uri, verb, o))
            except KeyError:
                pass


if __name__ == "__main__":
    QUDT().write_graph()
