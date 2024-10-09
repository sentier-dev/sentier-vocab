from rdflib.namespace import RDFS, SKOS, RDF
from rdflib import URIRef, Namespace, Literal

PRODUCTS = Namespace("https://vocab.sentier.dev/products/")

CUSTOM_PRODUCTS_DATA = [
    (
        URIRef(PRODUCTS + "electrolyzer"),
        RDF.type,
        SKOS.Concept
    ),
    (
        URIRef(PRODUCTS + "electrolyzer"),
        SKOS.broader,
        URIRef("http://data.europa.eu/xsp/cn2024/854330700080")
    ),
    (
        URIRef(PRODUCTS + "electrolyzer"),
        SKOS.prefLabel,
        Literal("Electrolyzer", lang="en")
    ),
    (
        URIRef(PRODUCTS + "electrolyzer"),
        SKOS.definition,
        Literal("An electrolyzer is a machine that uses electricity to drive a chemical reaction.", lang="en")
    ),
    (
        URIRef(PRODUCTS + "electrolyzer"),
        SKOS.related,
        URIRef("https://en.wikipedia.org/wiki/Electrolysis")
    ),
    (
        URIRef(PRODUCTS + "aec-electrolyzer"),
        RDF.type,
        SKOS.Concept
    ),
    (
        URIRef(PRODUCTS + "aec-electrolyzer"),
        SKOS.broader,
        URIRef(PRODUCTS + "electrolyzer")
    ),
    (
        URIRef(PRODUCTS + "aec-electrolyzer"),
        SKOS.prefLabel,
        Literal("Alkaline Electrolysis Cell Electrolyzer", lang="en")
    ),
    (
        URIRef(PRODUCTS + "aec-electrolyzer"),
        SKOS.definition,
        Literal("An electrolyzer with two electrodes operating in a liquid alkaline electrolyte.", lang="en")
    ),
    (
        URIRef(PRODUCTS + "aec-electrolyzer"),
        SKOS.related,
        URIRef("https://en.wikipedia.org/wiki/Alkaline_water_electrolysis")
    ),
    (
        URIRef(PRODUCTS + "pem-electrolyzer"),
        RDF.type,
        SKOS.Concept
    ),
    (
        URIRef(PRODUCTS + "pem-electrolyzer"),
        SKOS.broader,
        URIRef(PRODUCTS + "electrolyzer")
    ),
    (
        URIRef(PRODUCTS + "pem-electrolyzer"),
        SKOS.prefLabel,
        Literal("Proton Exchange Membrane Electrolyzer", lang="en")
    ),
    (
        URIRef(PRODUCTS + "pem-electrolyzer"),
        SKOS.definition,
        Literal("An electrolyzer with a solid polymer electrolyte and a proton exchange membrane.", lang="en")
    ),
    (
        URIRef(PRODUCTS + "pem-electrolyzer"),
        SKOS.related,
        URIRef("https://en.wikipedia.org/wiki/Proton_exchange_membrane_electrolysis")
    ),
    (
        URIRef(PRODUCTS + "soel-electrolyzer"),
        RDF.type,
        SKOS.Concept
    ),
    (
        URIRef(PRODUCTS + "soel-electrolyzer"),
        SKOS.broader,
        URIRef(PRODUCTS + "electrolyzer")
    ),
    (
        URIRef(PRODUCTS + "soel-electrolyzer"),
        SKOS.prefLabel,
        Literal("Solid Oxide Electrolyzer", lang="en")
    ),
    (
        URIRef(PRODUCTS + "soel-electrolyzer"),
        SKOS.definition,
        Literal("A solid oxide fuel cell that runs in regenerative mode to achieve the electrolysis of water.", lang="en")
    ),
    (
        URIRef(PRODUCTS + "soel-electrolyzer"),
        SKOS.related,
        URIRef("https://en.wikipedia.org/wiki/Solid_oxide_electrolyzer_cell")
    ),
    # Missing from Combined Nomenclature
    # tetraflouroethylene, not poly-
    (
        URIRef(PRODUCTS + "tetrafluoroethylene"),
        RDF.type,
        SKOS.Concept
    ),
    (
        URIRef(PRODUCTS + "tetrafluoroethylene"),
        SKOS.broader,
        URIRef("http://data.europa.eu/xsp/cn2024/290349000080")
    ),
    (
        URIRef(PRODUCTS + "tetrafluoroethylene"),
        SKOS.prefLabel,
        Literal("Tetrafluoroethylene", lang="en")
    ),
    (
        URIRef(PRODUCTS + "tetrafluoroethylene"),
        SKOS.related,
        URIRef("https://en.wikipedia.org/wiki/Tetrafluoroethylene")
    ),
    (
        URIRef(PRODUCTS + "tetrafluoroethylene"),
        SKOS.definition,
        Literal("Tetrafluoroethylene (TFE) is a fluorocarbon with the chemical formula C2F4. It is the simplest perfluorinated alkene. This gaseous species is used primarily in the industrial preparation of fluoropolymers (from Wikipedia)", lang="en")
    ),
    # Zeolite
    (
        URIRef(PRODUCTS + "zeolite"),
        RDF.type,
        SKOS.Concept
    ),
    (
        URIRef(PRODUCTS + "zeolite"),
        SKOS.broader,
        URIRef("http://data.europa.eu/xsp/cn2024/382400000080")
    ),
    (
        URIRef(PRODUCTS + "zeolite"),
        SKOS.prefLabel,
        Literal("Zeolite", lang="en")
    ),
    (
        URIRef(PRODUCTS + "zeolite"),
        SKOS.related,
        URIRef("https://en.wikipedia.org/wiki/Zeolite")
    ),
    (
        URIRef(PRODUCTS + "zeolite"),
        SKOS.definition,
        Literal("Zeolite is a family of several microporous, crystalline aluminosilicate materials commonly used as commercial adsorbents and catalysts (from Wikipedia)", lang="en")
    ),
]
