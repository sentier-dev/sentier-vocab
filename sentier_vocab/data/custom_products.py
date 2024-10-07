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
]
