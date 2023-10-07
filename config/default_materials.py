"""
This file contains the list of materials that will become demand methods.
To remove an entry, simply delete the line
To add an entry, make sure that it matches EXACTLY (but case insensitive)
with the activity's name in the database  
This list is designed for ecoinvent v3.9.1 and contains all of 
the activities that matched closest with EU CRM list 2023
Additional materials are also included, such as sand, water, gas, electricity and other 
items from "strategic materials" lists
"""


default_materials = [
    ("market for antimony", "antimony"),
    ("market for bauxite", "bauxite"),
    ("market for beryllium", "beryllium"),
    ("market for calcium borates", "borates"),
    ("market for cement, unspecified", "cement"),
    ("market for cobalt", "cobalt"),
    ("market for coke", "coke"),
    ("market for copper, anode", "copper"),
    ("market for copper, cathode", "copper"),
    # ("market for electricity, high voltage", "electricity"),
    # ("market for electricity, low voltage", "electricity"),
    # ("market for electricity, medium voltage", "electricity"),
    ("market for ferroniobium, 66% Nb", "niobium"),
    ("market for fluorspar, 97% purity", "fluorspar"),
    ("market for gallium, semiconductor-grade", "gallium"),
    ("market for gold", "gold"),
    ("market for graphite", "graphite"),
    ("market for hafnium sponge", "hafnium"),
    ("market for hafnium tetrachloride", "hafnium"),
    ("market for helium", "helium"),
    ("market for indium", "indium"),
    ("market for latex", "latex"),
    ("market for lithium carbonate", "lithium"),
    ("market for lithium sulfate", "lithium"),
    ("market for magnesium", "magnesium"),
    # ("market for natural gas, high pressure", "natural gas"),
    # ("market for natural gas, low pressure", "natural gas"),
    ("market for nickel, class 1", "nickel"),
    ("market for palladium", "palladium"),
    ("market for petroleum", "petroleum"),
    ("market for phosphate rock, beneficiated", "phosphate rock"),
    ("market for platinum", "platinum"),
    ("market for rare earth carbonate concentrate", "rare earth"),
    ("market for rare earth oxide concentrate, 50% REO", "rare earth"),
    ("market for rare earth oxide concentrate, 70% REO", "rare earth"),
    ("market for rhodium", "rhodium"),
    ("market for sand", "sand"),
    ("market for scandium oxide", "scandium"),
    ("market for silicon carbide", "silicon"),
    ("market for silicon tetrahydride", "silicon"),
    ("market for silicon, electronics grade", "silicon"),
    ("market for silicon, metallurgical grade", "silicon"),
    ("market for silicon, multi-Si, casted", "silicon"),
    ("market for silicon, single crystal, Czochralski process, electronics", "silicon"),
    ("market for silicon, single crystal, Czochralski process, photovoltaics", "silicon"),
    ("market for silicon, solar grade", "silicon"),
    ("market for silver", "silver"),
    ("market for sodium borates", "borates"),
    ("market for strontium sulfate, 90% SrSO4", "strontium"),
    ("market for tantalum concentrate, 30% Ta2O5", "tantalum"),
    ("market for tungsten concentrate", "tungsten"),
    ("market for vegetable oil, refined", "vegetable oil"),
    # ("market for tap water", "water"),
    # ("market for water, decarbonised", "water"),
    # ("market for water, ultrapure", "water"),	
    # ("market for water, deionised", "water"),	
    # ("market for water, completely softened", "water"),
    ("market for water, harvested from rainwater", "water"),	
    ("market for zinc", "zinc")
]
