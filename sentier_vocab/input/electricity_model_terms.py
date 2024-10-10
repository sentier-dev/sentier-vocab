from datetime import date

from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

CS = URIRef("https://vocab.sentier.dev/model-terms/emission-factor")

ELECTRICITY_MODEL_TERMS_DATA = [
    (CS, "type", "ConceptScheme"),
    (CS, "prefLabel", "Emission factor terms", "en"),
    (CS, "created", Literal(date(2024, 10, 10))),
    (CS, "creator", "Chris Mutel"),
    (CS, "description", "Terms related to technology emission factors", "en"),
    (CS, "subject", "Sentier.dev models"),
    (
        CS,
        "definition",
        "The production emission factor is the ratio of emissions produced to the amount of electricity generated.",
        "en",
    ),
    # Production emission factor
    ("prod-ef", "type", "Concept"),
    ("prod-ef", "broader", CS),
    ("prod-ef", "prefLabel", "Production emission factor", "en"),
    (
        "prod-ef",
        "definition",
        "The production emission factor is the ratio of emissions produced to the amount of electricity generated.",
        "en",
    ),
    # Bonsai production emission factor
    ("bonsai-prod-ef", "type", "Concept"),
    ("bonsai-prod-ef", "broader", CS),
    ("bonsai-prod-ef", "prefLabel", "Bonsai production emission factor", "en"),
    ("bonsai-prod-ef", "related", "https://lca.aau.dk/"),
    ("bonsai-prod-ef", "related", "https://github.com/BONSAMURAIS/"),
    (
        "bonsai-prod-ef",
        "definition",
        "The Bonsai production emission factor is the ratio of emissions produced to the amount of electricity generated based on data from Bonsai.",
        "en",
    ),
    # Bonsai supply chain emission factor
    ("bonsai-sc-ef", "type", "Concept"),
    ("bonsai-sc-ef", "broader", CS),
    ("bonsai-prod-ef", "related", "https://lca.aau.dk/"),
    ("bonsai-prod-ef", "related", "https://github.com/BONSAMURAIS/"),
    ("bonsai-sc-ef", "prefLabel", "Bonsai supply chain emission factor", "en"),
    (
        "bonsai-sc-ef",
        "definition",
        "The Bonsai supply chain emission factor is the ratio of emissions produced indirectly to the amount of electricity generated.",
        "en",
    ),
]
