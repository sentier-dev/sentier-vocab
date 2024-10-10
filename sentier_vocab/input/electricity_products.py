from rdflib.namespace import RDFS, SKOS, RDF
from rdflib import URIRef, Namespace, Literal

PRODUCTS = Namespace("https://vocab.sentier.dev/products/")

ELECTRICITY_PRODUCTS_DATA = [ 
    # Fossil fuel-based electrical energy
    ("fossil-fuel", "type", "Concept"),
    ("fossil-fuel", "broader", "http://data.europa.eu/xsp/cn2024/271600000080"),
    ("fossil-fuel", "prefLabel", "Fossil fuel-based electrical energy", "en-US"),
    ("fossil-fuel", "definition", "Fossil fuel-based electrical energy is electrical energy produced by incineration of fossil fuels.", "en"),
    ("fossil-fuel", "related", "https://en.wikipedia.org/wiki/Fossil_fuel"),
    # Fossil oil-based electrical energy
    ("fossil-oil", "type", "Concept"),
    ("fossil-oil", "broader", PRODUCTS + "fossil-energy"),
    ("fossil-oil", "prefLabel", "Fossil oil-based electrical energy", "en"),
    ("fossil-oil", "definition", "Fossil oil-based electrical energy is electrical energy produced by the combustion of fossil oils.", "en"),
    ("fossil-oil", "related", "https://en.wikipedia.org/wiki/Petroleum"),
    # Electrical energy from (crude) oil
    ("crude-oil", "type", "Concept"),
    ("crude-oil", "broader", PRODUCTS + "fossil-oil"),
    ("crude-oil", "prefLabel", "Electrical energy from crude oil", "en"),
    ("crude-oil", "definition", "Electrical energy from crude oil refers to electricity generated from the combustion of crude oil.", "en"),
    ("crude-oil", "related", "https://en.wikipedia.org/wiki/Petroleum"),
    # Electrical energy from oil shale
    ("oil-shale", "type", "Concept"),
    ("oil-shale", "broader", PRODUCTS + "fossil-oil"),
    ("oil-shale", "prefLabel", "Electrical energy from oil shale", "en"),
    ("oil-shale", "definition", "Electrical energy from oil shale is generated from the processing and combustion of oil shale.", "en"),
    ("oil-shale", "related", "https://en.wikipedia.org/wiki/Oil_shale"),
    # Fossil gas-based electrical energy
    ("fossil-gas", "type", "Concept"),
    ("fossil-gas", "broader", PRODUCTS + "fossil-fuel"),
    ("fossil-gas", "prefLabel", "Natural gas-based electrical energy", "en"),
    ("fossil-gas", "definition", "Natural gas-based electrical energy is electrical energy produced through the combustion of natural gas.", "en"),
    ("fossil-gas", "related", "https://en.wikipedia.org/wiki/Natural_gas"),
    # Electrical energy from natural gas
    ("natural-gas", "type", "Concept"),
    ("natural-gas", "broader", PRODUCTS + "fossil-gas"),
    ("natural-gas", "prefLabel", "Electrical energy from natural gas", "en"),
    ("natural-gas", "definition", "Electrical energy from natural gas refers to electricity generated from the combustion of natural gas.", "en"),
    ("natural-gas", "related", "https://en.wikipedia.org/wiki/Natural_gas"),
    # Electrical energy from coal seam gas
    ("coalbed-gas", "type", "Concept"),
    ("coalbed-gas", "broader", PRODUCTS + "fossil-gas"),
    ("coalbed-gas", "prefLabel", "Electrical energy from coal seam gas", "en"),
    ("coalbed-gas", "definition", "Electrical energy from coal seam gas is generated through the combustion of coal seam gas.", "en"),
    ("coalbed-gas", "related", "https://en.wikipedia.org/wiki/Coalbed_methane"),
    # Coal-based electrical energy
    ("fossil-coal", "type", "Concept"),
    ("fossil-coal", "broader", PRODUCTS + "fossil-fuel"),
    ("fossil-coal", "prefLabel", "Coal-based electrical energy", "en"),
    ("fossil-coal", "definition", "Coal-based electrical energy is electrical energy produced by the combustion of coal.", "en"),
    ("fossil-coal", "related", "https://en.wikipedia.org/wiki/Coal-fired_power_station"),
    # Electrical energy from hard coal
    ("hard-coal", "type", "Concept"),
    ("hard-coal", "broader", PRODUCTS + "fossil-coal"),
    ("hard-coal", "prefLabel", "Electrical energy from hard coal", "en"),
    ("hard-coal", "definition", "Electrical energy from hard coal is generated from the combustion of hard coal.", "en"),
    ("hard-coal", "related", "https://en.wikipedia.org/wiki/Coal-fired_power_station"),
    # Electrical energy from brown coal/lignite
    ("lignite", "type", "Concept"),
    ("lignite", "broader", PRODUCTS + "fossil-coal"),
    ("lignite", "prefLabel", "Electrical energy from brown coal/lignite", "en"),
    ("lignite", "definition", "Electrical energy from brown coal/lignite is generated from the combustion of brown coal or lignite.", "en"),
    ("lignite", "related", "https://en.wikipedia.org/wiki/Lignite"),
    # Electrical energy from peat
    ("peat", "type", "Concept"),
    ("peat", "broader", PRODUCTS + "fossil-fuel"),
    ("peat", "prefLabel", "Electrical energy from peat", "en"),
    ("peat", "definition", "Electrical energy from peat is generated through the combustion of peat.", "en"),
    ("peat", "related", "https://en.wikipedia.org/wiki/Peat"),  

    # Renewable electrical energy
    ("renewable-energy", "type", "Concept"),
    ("renewable-energy", "broader", "http://data.europa.eu/xsp/cn2024/271600000080"),
    ("renewable-energy", "prefLabel", "Renewable electrical energy", "en-US"),
    ("renewable-energy", "definition", "Renewable electrical energy is electrical energy produced from renewable resources.", "en"),
    ("renewable-energy", "related", "https://en.wikipedia.org/wiki/Renewable_energy"),
    ("renewable-energy", "exactMatch", "http://openenergy-platform.org/ontology/oeo/OEO_00010384"),
    # Wind-based electrical energy
    ("wind-energy", "type", "Concept"),
    ("wind-energy", "broader", PRODUCTS + "renewable-energy"),
    ("wind-energy", "prefLabel", "Electricity from wind energy", "en-US"),
    ("wind-energy", "definition", "Electricity from wind energy is electrical energy produced by converting wind energy into electricity through wind turbines.", "en"),
    ("wind-energy", "related", "https://en.wikipedia.org/wiki/Wind_power"),
    # Electrical energy from offshore wind
    ("offshore", "type", "Concept"),
    ("offshore", "broader", PRODUCTS + "wind-energy"),
    ("offshore", "prefLabel", "Electricity from offshore wind energy", "en-US"),
    ("offshore", "definition", "Electrical energy from offshore wind is generated by wind turbines located in bodies of water.", "en"),
    ("offshore", "related", "https://en.wikipedia.org/wiki/Offshore_wind_power"),
    # Electrical energy from onshore wind
    ("onshore", "type", "Concept"),
    ("onshore", "broader", PRODUCTS + "wind-energy"),
    ("onshore", "prefLabel", "Electricity from onshore wind energy", "en-US"),
    ("onshore", "definition", "Electricity from onshore wind energy is generated by wind turbines located on land.", "en"),
    ("onshore", "related", "https://en.wikipedia.org/wiki/Wind_power"),
    # Water-based electrical energy
    ("hydropower", "type", "Concept"),
    ("hydropower", "broader", PRODUCTS + "renewable-energy"),
    ("hydropower", "prefLabel", "Electricity from hydropower", "en-US"),
    ("hydropower", "definition", "Electricity from hydropower is electrical energy generated through the use of water resources.", "en"),
    ("hydropower", "related", "https://en.wikipedia.org/wiki/Hydroelectricity"),
    # Electrical energy from hydro water reservoirs
    ("hydro-reservoirs", "type", "Concept"),
    ("hydro-reservoirs", "broader", PRODUCTS + "hydropower"),
    ("hydro-reservoirs", "prefLabel", "Electrical energy from hydro water reservoirs", "en-US"),
    ("hydro-reservoirs", "definition", "Electrical energy from hydro water reservoirs is generated using stored water in reservoirs to drive hydro turbines.", "en"),
    ("hydro-reservoirs", "related", "https://en.wikipedia.org/wiki/Reservoir"),
    # Electrical energy from pumped storage hydro
    ("pumped-storage", "type", "Concept"),
    ("pumped-storage", "broader", PRODUCTS + "hydropower"),
    ("pumped-storage", "prefLabel", "Electrical energy from pumped storage hydro", "en-US"),
    ("pumped-storage", "definition", "Electrical energy from pumped storage hydro is generated through a two-reservoir system where water is pumped to a higher elevation for storage and released to generate electricity.", "en"),
    ("pumped-storage", "related", "https://en.wikipedia.org/wiki/Pumped-storage_hydroelectricity"),
    # Electrical energy from run-of-river and poundage hydro
    ("run-of-river", "type", "Concept"),
    ("run-of-river", "broader", PRODUCTS + "hydropower"),
    ("run-of-river", "prefLabel", "Electrical energy from run-of-river and poundage hydro", "en-US"),
    ("run-of-river", "definition", "Electrical energy from run-of-river and poundage hydro is generated without large reservoirs, utilizing the natural flow of rivers.", "en"),
    ("run-of-river", "related", "https://en.wikipedia.org/wiki/Run-of-the-river_hydroelectricity"),
    # Electrical energy from marine sources
    ("marine", "type", "Concept"),
    ("marine", "broader", PRODUCTS + "hydropower"),
    ("marine", "prefLabel", "Electrical energy from marine sources", "en-US"),
    ("marine", "definition", "Electrical energy from marine sources is generated from ocean and tidal forces, exploiting kinetic energy.", "en"),
    ("marine", "related", "https://en.wikipedia.org/wiki/Marine_energy"),
    # Solar-based electrical energy
    ("solar", "type", "Concept"),
    ("solar", "broader", PRODUCTS + "renewable-energy"),
    ("solar", "prefLabel", "Solar-based electrical energy", "en-US"),
    ("solar", "definition", "Solar-based electrical energy is generated by converting sunlight into electricity through photovoltaic cells or solar thermal systems.", "en"),
    ("solar", "related", "https://en.wikipedia.org/wiki/Solar_power"),
    ("solar", "exactMatch", "http://openenergy-platform.org/ontology/oeo/OEO_00010419"),
    # Other renewable electrical energy
    ("other-renewable", "type", "Concept"),
    ("other-renewable", "broader", PRODUCTS + "renewable-energy"),
    ("other-renewable", "prefLabel", "Other renewable electrical energy", "en-US"),
    ("other-renewable", "definition", "Other renewable electrical energy includes electricity generated from sources such as geothermal and biomass.", "en"),
    # Electrical energy from geothermal sources
    ("geothermal", "type", "Concept"),
    ("geothermal", "broader", PRODUCTS + "other-renewable"),
    ("geothermal", "prefLabel", "Electrical energy from geothermal sources", "en-US"),
    ("geothermal", "definition", "Electrical energy from geothermal sources is generated by harnessing heat from the earth's interior.", "en"),
    ("geothermal", "related", "https://en.wikipedia.org/wiki/Geothermal_energy"),
    # Electrical energy from biomass
    ("biomass", "type", "Concept"),
    ("biomass", "broader", PRODUCTS + "other-renewable"),
    ("biomass", "prefLabel", "Electrical energy from biomass", "en-US"),
    ("biomass", "definition", "Electrical energy from biomass is generated by burning organic materials such as plant and animal waste to produce electricity.", "en"),
    ("biomass", "related", "https://en.wikipedia.org/wiki/Bioenergy"),
    # Electrical energy from other renewable sources
    ("other-renewable-sources", "type", "Concept"),
    ("other-renewable-sources", "broader", PRODUCTS + "other-renewable"),
    ("other-renewable-sources", "prefLabel", "Electrical energy from other renewable sources", "en-US"),
    ("other-renewable-sources", "definition", "Electrical energy from other renewable sources includes electricity generated from various innovative renewable technologies.", "en"),

    # Other electrical energy
    ("other", "type", "Concept"),
    ("other", "broader", "http://data.europa.eu/xsp/cn2024/271600000080"),
    ("other", "prefLabel", "Other electrical energy", "en-US"),
    ("other", "definition", "Other electrical energy includes various forms of electrical energy generation not classified as renewable or fossil fuel-based.", "en"),
    # Nuclear-based electrical energy
    ("nuclear", "type", "Concept"),
    ("nuclear", "broader", "http://data.europa.eu/xsp/cn2024/271600000080"),
    ("nuclear", "prefLabel", "Other electrical energy", "en-US"),
    ("nuclear", "definition", "Nuclear power is the generation of electricity through the process of nuclear fission, where atomic nuclei are split to release energy.", "en"),
    ("nuclear", "related", "https://en.wikipedia.org/wiki/Nuclear_power"),
    ("nuclear", "exactMatch", "http://openenergy-platform.org/ontology/oeo/OEO_00010417"),
    # Waste-based electrical energy
    ("waste", "type", "Concept"),
    ("waste", "broader", "http://data.europa.eu/xsp/cn2024/271600000080"),
    ("waste", "prefLabel", "Waste-based electrical energy", "en-US"),
    ("waste", "definition", "Waste-based electrical energy is generated by converting waste materials into electricity, typically through incineration or anaerobic digestion.", "en"),
    ("waste", "related", "https://en.wikipedia.org/wiki/Waste-to-energy"),

    # Electricity mix
    ("electricity-mix", "type", "Concept"),
    ("electricity-mix", "broader", "http://data.europa.eu/xsp/cn2024/271600000080"),
    ("electricity-mix", "prefLabel", "Electricity mix", "en-US"),
    ("electricity-mix", "definition", "Electricity mix is the combination of different energy technologies, including renewables and non-renewables, used for electricity generation.", "en"),
]