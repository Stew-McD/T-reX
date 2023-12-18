"""
queries_materials Module
========================

This module contains the list of materials that will be used to create demand methods in the WasteAndMaterialFootprint tool. The materials are specifically chosen to match with the activities in the ecoinvent v3.9.1 database (and the future databases made with premise) and to align with the EU CRM list 2023. Additional strategic materials are also included, as well as other materials of interest.

Note:
-----
- The search function in `SearchMaterial.py` uses 'startswith', so it will catch all activities that start with the material name.
- The comma in material names is important for filtering specific activities in the database.
- If an intermediate product is included, the inputs and outputs might cancel out, resulting in a zero result.

Author: Stewart Charles McDowall
Email: s.c.mcdowall@cml.leidenuniv.nl
GitHub: Stew-McD
Institution: CML, Leiden University
Licence: The Unlicense



queries_materials
-----------------
List of tuples where each tuple contains the activity name (as appears in the database) and its corresponding material category. This list is used for creating demand methods in the WasteAndMaterialFootprint tool.
"""

queries_materials = [
    ("market for aluminium", "aluminium"),
    ("market for antimony", "antimony"),
    ("market for bauxite", "bauxite"),
    ("market for beryllium", "beryllium"),
    ("market for bismuth", "bismuth"),
    ("market for cadmium", "cadmium"),
    ("market for calcium borates", "borates"),
    ("market for cement", "cement"),
    ("market for cerium", "cerium"),
    ("market for chromium", "chromium"),
    ("market for coal", "coal"),
    ("market for cobalt", "cobalt"),
    ("market for coke", "coke"),
    ("market for copper", "copper"),
    ("market for dysprosium", "dysprosium"),
    ("market for erbium", "erbium"),
    ("market for europium", "europium"),
    ("market for electricity,", "electricity"),
    ("market for ferroniobium,", "niobium"),
    ("market for fluorspar,", "fluorspar"),
    ("market for gadolinium", "gadolinium"),
    ("market for gallium", "gallium"),
    ("market for gold", "gold"),
    ("market for graphite", "graphite"),
    ("market for hafnium", "hafnium"),
    ("market for helium", "helium"),
    ("market for holmium", "holmium"),
    ("market for hydrogen,", "hydrogen"),
    ("market for indium", "indium"),
    ("market for latex", "latex"),
    ("market for lithium", "lithium"),
    ("market for magnesium", "magnesium"),
    ("market for natural gas,", "natural gas"),
    ("market for nickel", "nickel"),
    ("market for palladium", "palladium"),
    ("market for petroleum", "petroleum"),
    ("market for phosphate", "phosphate rock"),
    ("market for platinum", "platinum"),
    ("market for rare earth", "rare earth"),
    ("market for rhodium", "rhodium"),
    ("market for sand", "sand"),
    ("market for selenium", "selenium"),
    ("market for scandium", "scandium"),
    ("market for silicon", "silicon"),
    ("market for silver", "silver"),
    ("market for sodium borates", "borates"),
    ("market for strontium", "strontium"),
    ("market for tantalum", "tantalum"),
    ("market for tellurium", "tellurium"),
    ("market for tin", "tin"),
    ("market for titanium", "titanium"),
    ("market for uranium", "uranium"),
    ("market for tungsten", "tungsten"),
    ("market for vanadium", "vanadium"),
    ("market for vegetable oil,", "vegetable oil"),
    ("market for tap water", "water"),
    ("market for water,", "water"),
    ("market for zinc", "zinc"),
    ("market for zirconium", "zirconium"),
]
