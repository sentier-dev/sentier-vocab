from rdflib.namespace import RDFS, SKOS, RDF
from rdflib import URIRef, Namespace, Literal

PRODUCTS = Namespace("https://vocab.sentier.dev/products/electronics/")
MODEL_TERMS = Namespace("https://vocab.sentier.dev/model-terms/electronics/")

PCB_PRODUCTS_DATA = [ 
    ("electronics_factory", "type", "Concept"),
    ("electronics_factory", "prefLabel", "Electronics factory", "en"),
    ("electronics_factory", "definition", "A factory which makes various types of electronics and electronic components, including PCBs, which are the best kind.", "en"),
    ("electronics_factory", "related", "https://fr.wikipedia.org/wiki/Fabricant_de_composant_%C3%A9lectronique"),
    # Printed Circuit Board
    (URIRef("http://data.europa.eu/xsp/cn2024/853400000080"), "altLabel", "Printed circuit board", "en"),
    (URIRef("http://data.europa.eu/xsp/cn2024/853400000080"), "related", "https://en.wikipedia.org/wiki/Printed_circuit_board"),
    # Heat emmission factor
    (URIRef("https://vocab.sentier.dev/products/energy/heat"), "type", "Concept"),
    (URIRef("https://vocab.sentier.dev/products/energy/heat"), "prefLabel", "Heat", "en"),
    (URIRef("https://vocab.sentier.dev/products/energy/heat"), "related", "https://en.wikipedia.org/wiki/Heat"),
]

PCB_MODEL_TERMS_DATA = [
    ("surface_finish", "type", "Concept"),
    ("surface_finish", "prefLabel", "Surface finish type (usually silver, nickel-gold, or tin)", "en"),
    ("surface_finish", "definition", "This is the surface on pcb taken by all pads and vias, finished by a coating", "en"),
    ("surface_finish", "related", "https://en.wikipedia.org/wiki/Printed_circuit_board#Plating_and_coating"),
]
