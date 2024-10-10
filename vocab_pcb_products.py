from rdflib.namespace import RDFS, SKOS, RDF
from rdflib import URIRef, Namespace, Literal

PRODUCTS = Namespace("https://vocab.sentier.dev/products/")

PCB_PRODUCTS_DATA = [ 
    # electronic factory
    ("electronic_factory", "type", "Concept"),
    ("electronic_factory", "broader", PRODUCTS + "pcb"),
    ("electronic_factory", "prefLabel", "electronic factory", "en-US"),
    ("electronic_factory", "definition", "Impacts of the creation and use of one electronic factory", "en"),
    ("electronic_factory", "related", "https://fr.wikipedia.org/wiki/Fabricant_de_composant_%C3%A9lectronique"),

    # Printed Circuit Board
    ("pcb", "type", "Concept"),
    ("pcb", "broader", PRODUCTS), 
    ("pcb", "prefLabel", "printed circuit board", "en-US"),
    ("pcb", "definition", "Printed Circuit Board used for all kind of electronical uses", "en"),
    ("pcb", "related", "https://en.wikipedia.org/wiki/Printed_circuit_board"),
    # Fossil oil-based electrical energy
    ("electricity", "type", "Concept"),
    ("electricity", "broader", PRODUCTS),
    ("electricity", "prefLabel", "electricity", "en"),
    ("electricity", "definition", "electricity based on electrical mix.", "en"),
    ("electricity", "related", "https://en.wikipedia.org/wiki/Electricity"),
       # Heat emmission factor
    ("heat", "type", "Concept"),
    ("heat", "broader", "https://vocab.sentier.dev/model-terms/energy"),
    ("heat", "prefLabel", "Heat", "en-US"),
    ("heat", "definition", "Heat", "en"),
    ("heat", "related", "https://en.wikipedia.org/wiki/Heat"),
    [
    # surface of finish for 1m2 of PCB
    ("pcb/surface_finish", "type", "Concept"),
    ("pcb/surface_finish", "broader", PRODUCTS + "pcb"),
    ("pcb/surface_finish", "prefLabel", "Surface finish for 1m2 of PCB", "en-US"),
    ("pcb/surface_finish", "definition", "This is the surface on pcb taken by all pads and vias, finished by a coating", "en"),
    ("pcb/surface_finish", "related", "https://en.wikipedia.org/wiki/Printed_circuit_board#Plating_and_coating"),

 
] 

]