import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS, XSD
from pathlib import Path


def generate_mrf_turtles(param_data_path,output_file_path):


    preferred_labels = {
        'NIR HDPE':'near infrared sorting machine of HDPE plastics',
        'NIR PET':'near infrared sorting machine of PET plastics',
        'glass breaker':'glass breaker sorting machine',
        'disc screen 1':"disc screen sorting machine",
        'disc screen 2':"disc screen sorting machine",
        'disc screen 3':"disc screen sorting machine",
        'eddy':"eddy current separator",
        'magnet':'magnet sorting machine for ferrous metals',
        'vacuum':'vacuum sorting machine for film plastic',
        'optical glass':"optical sorting machine for glass",
                        }
    
    disc_descr = ("An inclined plane filled with a series of parallel rods "
         + "with discs spread along each rod such that large materials travel "  
         + "over the top while smaller materials fall between the discs")
    
    opticalglass_decr = " ".join(["Identifies pre-determined material(s) using optical",
    "technology (e.g., cameras, lasers, sensors) and removes the identified material" 
    "from the stream using bursts of compressed air"])

    description = {
        'eddy':"Uses magnetic fields to remove aluminum and other non-ferrous metals",
        'magnet':"Uses magnetic fields to remove ferrous metals",
        'disc screen 1':disc_descr,
        'disc screen 2':disc_descr,
        'disc screen 3':disc_descr,
        'optical glass':opticalglass_decr,
    }



    # New graph
    g = Graph()

    # Set up namespaces
    #mrf_equipment_url = "https://vocab.sentier.dev/model-terms/mrf-equipment/"
    #mrf_url = "https://vocab.sentier.dev/products/material-recovery-facility/"
    units = Namespace("https://vocab.sentier.dev/units/")
    qudt = Namespace("http://qudt.org/schema/qudt/")
    sorting_machines = Namespace("http://data.europa.eu/xsp/cn2024/847410000080")
    model_terms = Namespace("https://vocab.sentier.dev/model-terms/generic")

    g.bind("units", units)
    g.bind("qudt", qudt)
    g.bind("sorting_machines", sorting_machines)
    g.bind("skos", SKOS)

    # the existing Efficiency concept in dds vocabulary
    efficiency_qk = URIRef("https://vocab.sentier.dev/units/quantity-kind/Efficiency")
    sorting_machine = URIRef("https://publications.europa.eu/resource/authority/cpv/cpv/43411000")
    
    sequence = URIRef("http://semanticscience.org/resource/SIO_001118")


    # make the concept thingy
    scheme = URIRef(sorting_machines)

    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    
    # add general concepts

    # sequence
    g.add((URIRef("https://vocab.sentier.dev/model-terms/generic/sequence"),
          RDF.type,SKOS.Concept))
    
    g.add((URIRef("https://vocab.sentier.dev/model-terms/generic/sequence"),
          SKOS.exactMatch,sequence))

    # mixed waste 


    # sorting machines
    path_to_file = Path(__file__).parent / param_data_path
    df = pd.read_csv(path_to_file,sep=';')

    for _equipment in df.equipment.unique():
        
        uri = URIRef(f"{sorting_machines}{_equipment.replace(' ', '_')}")
        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, SKOS.prefLabel, 
               Literal(preferred_labels.get(_equipment,_equipment), lang="en")))
        #g.add((uri, SKOS.inScheme, scheme))
        g.add((uri, qudt.hasQuantityKind, efficiency_qk))
        g.add((uri, SKOS.broader, sorting_machine))

        if _equipment in description:
            g.add((uri,SKOS.definition,
                   Literal(description.get(_equipment),lang="en")))

    g.serialize(destination=output_file_path, format="turtle")


if __name__ == '__main__':

    output_file = Path(__file__).parent / "output"/'material_recover_facility.ttl'
    input_file = Path(__file__).parent /'input'/ "corrected_mrf_equipment_efficiency.csv"
    
    generate_mrf_turtles(input_file,output_file)