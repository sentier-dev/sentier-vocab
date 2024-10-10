import polars as pl
from rdflib import URIRef, Graph, Namespace
from rdflib.namespace import RDF, SKOS
from rdflib import Literal
from rdflib.namespace import XSD
from skosify import infer
import sentier_data_tools as sdt
import os
import zipfile
from urllib.request import urlretrieve

"""
The data for this was found at geonames' site, but it's much too large to put onto git.
For the data used to generate the dataframe for the entire world, look here:
384MB, unpacks to 1.6 GB https://download.geonames.org/export/dump/allCountries.zip
For the hierarchy dataframe, look here:
2MB, unpacks to 9MB https://download.geonames.org/export/dump/hierarchy.zip

set the world_path to where you stored allCountries.txt, and hierarchy_path to wherever hierarchy.txt is.
"""

def generateGeonameVocabulary(world_path: str, hierarchy_path: str):
    
    # ##  THIS PART FETCHES AND EXTRACTS.
    # temp_dir = os.path.join(os.curdir,"temp")
    # if not os.path.exists(temp_dir):
    #     os.mkdir(temp_dir)
    
    # hier_zip = os.path.realpath(os.path.join(temp_dir,"hierarchy.zip"))
    # hierarchy_path = os.path.realpath(os.path.join(temp_dir,"hierarchy.txt"))
    # hierarchy_url = "https://download.geonames.org/export/dump/hierarchy.zip"

    # world_zip = os.path.realpath(os.path.join(temp_dir,"allCountries.zip"))
    # world_path = os.path.realpath(os.path.join(temp_dir,"allCountries.txt"))
    # world_url = "https://download.geonames.org/export/dump/allCountries.zip"

    # urlretrieve(hierarchy_url,hier_zip)

    # urlretrieve(world_url,world_zip)

    # with zipfile.ZipFile(hier_zip, 'r') as zip_ref:
    #     zip_ref.extractall(temp_dir)
    
    # with zipfile.ZipFile(world_zip, 'r') as zip_reff:
    #     zip_reff.extractall(temp_dir)

    # ##FETCHING AND EXTRACTING COMPLETED

    GEOSPACES = "https://sws.geonames.org/"
    GN = Namespace("http://www.geonames.org/ontology#")

    all_schema = pl.Schema({
        "geonameid":pl.Int64,
        "name":pl.String,
        "asciiname":pl.String,
        "alternatenames":pl.String,
        "latitude":pl.Float32,
        "longitude":pl.Float32,
        "feature_class":pl.String,
        "feature_code":pl.String,
        "country_code":pl.String,
        "cc2":pl.String,
        "admin1_code":pl.String,
        "admin2_code":pl.String,
        "admin3_code":pl.String,
        "admin4_code":pl.String,
        "population":pl.Int64,
        "elevation":pl.Int16,
        "dem":pl.Int64,
        "timezone":pl.String,
        "modification_date":pl.Date
    })

    world_frame = pl.scan_csv(source=world_path,has_header=False,separator='\t',schema=all_schema)

    ##In the SQL here you can actually expand or narrow what you're going to model.
    ##See more at https://download.geonames.org/export/dump/readme.txt, scroll down to "feature classes"
    ##to isolate only countries, use "where feature_code = 'PCLI'"
    
    hierarchy_schema = pl.Schema({
        "parent":pl.Int64,
        "child":pl.Int64,
        "admin1_code":pl.String
    })

    hierarchy = pl.scan_csv(hierarchy_path,schema=hierarchy_schema,separator='\t')

    filtered_world = world_frame.sql("select * from self where feature_code in ('PCLI', 'ADM1', 'RGN')").collect()

    world = Graph()

    for item in filtered_world.iter_rows():
        uri = URIRef(GEOSPACES + str(item[0]))
        pref_name = Literal(item[1])
        alt_names = []
        #if item[3]:
        #   alt_names = item[3].split(",")
        world.add((
            uri,
            RDF.type,
            SKOS.Concept
        ))
        world.add((
            uri,
            SKOS.prefLabel,
            pref_name
        ))
        world.add((
            uri,
            GN.countryCode,
            Literal(item[8])
        ))
        children = hierarchy.sql(f"select * from self where parent = {item[0]}").collect()
        if len(children) > 0:
            for child in children.iter_rows():
                if not filtered_world.filter(pl.col('geonameid') == child[1]).is_empty():
                    world.add((
                        uri,
                        SKOS.narrower,
                        URIRef(GEOSPACES + str(child[1]))
                    ))


    infer.skos_hierarchical(world)
    world.serialize(destination='output/geonames-iri.ttl')