from rdflib.namespace import RDFS, SKOS, RDF
from rdflib import URIRef, Namespace, Literal

PRODUCTS = Namespace("https://vocab.sentier.dev/products/")

CUSTOM_PRODUCTS_DATA = [
    ("electrolyzer", "type", "Concept"),
    ("electrolyzer", "broader", "http://data.europa.eu/xsp/cn2024/854330700080"),
    ("electrolyzer", "prefLabel", "Electrolyzer", "en-US"),
    ("electrolyzer", "prefLabel", "Electrolyzer", "en-GB"),
    ("electrolyzer", "definition", "An electrolyzer is a machine that uses electricity to drive a chemical reaction.", "en"),
    ("electrolyzer", "related", "https://en.wikipedia.org/wiki/Electrolysis"),
    ("aec-electrolyzer", "type", "Concept"),
    ("aec-electrolyzer", "broader", PRODUCTS + "electrolyzer"),
    ("aec-electrolyzer", "prefLabel", "Alkaline Electrolysis Cell Electrolyzer", "en"),
    ("aec-electrolyzer", "definition", "An electrolyser with two electrodes operating in a liquid alkaline electrolyte.", "en"),
    ("aec-electrolyzer", "related", "https://en.wikipedia.org/wiki/Alkaline_water_electrolysis"),
    ("pem-electrolyzer", "type", "Concept"),
    ("pem-electrolyzer", "broader", PRODUCTS + "electrolyzer"),
    ("pem-electrolyzer", "prefLabel", "Proton Exchange Membrane Electrolyser", "en-GB"),
    ("pem-electrolyzer", "prefLabel", "Proton Exchange Membrane Electrolyzer", "en-US"),
    ("pem-electrolyzer", "definition", "An electrolyser with a solid polymer electrolyte and a proton exchange membrane.", "en"),
    ("pem-electrolyzer", "related", "https://en.wikipedia.org/wiki/Proton_exchange_membrane_electrolysis"),
    ("soel-electrolyzer", "type", "Concept"),
    ("soel-electrolyzer", "broader", PRODUCTS + "electrolyzer"),
    ("soel-electrolyzer", "prefLabel", "Solid Oxide Electrolyzer", "en"),
    ("soel-electrolyzer", "definition", "A solid oxide fuel cell that runs in regenerative mode to achieve the electrolysis of water.", "en"),
    ("soel-electrolyzer", "related", "https://en.wikipedia.org/wiki/Solid_oxide_electrolyzer_cell"),
    # Missing from Combined Nomenclature
    # tetraflouroethylene, not poly-
    ("tetrafluoroethylene", "type", "Concept"),
    ("tetrafluoroethylene", "broader", "http://data.europa.eu/xsp/cn2024/290349000080"),
    ("tetrafluoroethylene", "prefLabel", "Tetrafluoroethylene", "en"),
    ("tetrafluoroethylene", "related", "https://en.wikipedia.org/wiki/Tetrafluoroethylene"),
    ("tetrafluoroethylene", "definition", "Tetrafluoroethylene (TFE) is a fluorocarbon with the chemical formula C2F4. It is the simplest perfluorinated alkene. This gaseous species is used primarily in the industrial preparation of fluoropolymers (from Wikipedia)", "en"),
    # Zeolite
    ("zeolite", "type", "Concept"),
    ("zeolite", "broader", "http://data.europa.eu/xsp/cn2024/382400000080"),
    ("zeolite", "prefLabel", "Zeolite", "en"),
    ("zeolite", "related", "https://en.wikipedia.org/wiki/Zeolite"),
    ("zeolite", "definition", "Zeolite is a family of several microporous, crystalline aluminosilicate materials commonly used as commercial adsorbents and catalysts (from Wikipedia)", "en"),
]
