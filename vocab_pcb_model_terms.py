from rdflib.namespace import RDFS, SKOS, RDF
from rdflib import URIRef, Namespace, Literal

MODEL_TERMS = Namespace("https://vocab.sentier.dev/model-terms/")

PCB_MODEL_TERMS_DATA = [
    # electronic factory
    ("electronic_factory", "type", "Concept"),
    ("electronic_factory", "broader", "https://vocab.sentier.dev/model-terms/pcb"),
    ("electronic_factory", "prefLabel", "electronic factory", "en-US"),
    ("electronic_factory", "definition", "Impacts of the creation and use of one electronic factory", "en"),
    # surface of finish for 1m2 of PCB
    ("pcb/surface_finish", "type", "Concept"),
    ("pcb/surface_finish", "broader", "https://vocab.sentier.dev/model-terms/pcb"),
    ("pcb/surface_finish", "prefLabel", "Surface finish for 1m2 of PCB", "en-US"),
    ("pcb/surface_finish", "definition", "This is the surface on pcb taken by all pads and vias, finished by a coating", "en"),
    # Heat emmission factor
    ("heat", "type", "Concept"),
    ("heat", "broader", "https://vocab.sentier.dev/model-terms/energy"),
    ("heat", "prefLabel", "Heat", "en-US"),
    ("heat", "definition", "Heat", "en"),
] 