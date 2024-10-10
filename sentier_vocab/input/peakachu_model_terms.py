from rdflib.namespace import RDFS, SKOS, RDF
from rdflib import URIRef, Namespace, Literal

MODEL_TERMS = Namespace("https://vocab.sentier.dev/model-terms/")

ELECTRICITY_MODEL_TERMS_DATA = [
    # Production emission factor
    ("prod-ef", "type", "Concept"),
    ("prod-ef", "broader", "https://vocab.sentier.dev/model-terms/energy"),
    ("prod-ef", "prefLabel", "Production emission factor", "en-US"),
    ("prod-ef", "definition", "The production emission factor is the ratio of emissions produced to the amount of electricity generated.", "en"),
    # Bonsai production emission factor
    ("bonsai-prod-ef", "type", "Concept"),
    ("bonsai-prod-ef", "broader", "https://vocab.sentier.dev/model-terms/energy"),
    ("bonsai-prod-ef", "prefLabel", "Bonsai production emission factor", "en-US"),
    ("bonsai-prod-ef", "definition", "The bonsay production emission factor is the ratio of emissions produced to the amount of electricity generated based on data from Bonsai.", "en"),
    # Bonsai supply chain emission factor
    ("bonsai-sc-ef", "type", "Concept"),
    ("bonsai-sc-ef", "broader", "https://vocab.sentier.dev/model-terms/energy"),
    ("bonsai-sc-ef", "prefLabel", "Bonsai supply chain emission factor", "en-US"),
    ("bonsai-sc-ef", "definition", "The bonsai supply chain emission factor is the ratio of emissions produced indirectly to the amount of electricity generated.", "en"),
]