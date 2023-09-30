#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
|===============================================================|
| File: FutureScenarios.py                                      |
| Project: WasteAndMaterialFootprint                            |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint   |
| Description: <<description>>                                  |
|---------------------------------------------------------------|
| File Created: Friday, 22nd September 2023 11:51:18 am         |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                                |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Friday, 22nd September 2023 12:43:24 pm        |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|
"""

# Based on R.Sacchi's tutorial:
# https://github.com/polca/premise/blob/master/examples/examples.ipynb

from pathlib import Path
import os
import premise as pm
import bw2data as bd
from premise_gwp import add_premise_gwp

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
# os.environ["BRIGHTWAY2_DIR"] = os.path.expanduser("~") + '/bw'

# Make a new project
base_project = "default"
new_project = "SSP125"

delete_existing = True

if new_project in bd.projects and delete_existing:
    bd.projects.delete_project(new_project, True)
    print(f"Deleted existing project {new_project}")
    bd.projects.set_current(base_project)
    bd.projects.copy_project(new_project)
    print(f"Created new project {new_project} from {base_project}")

elif new_project in bd.projects and not delete_existing:
    print(f"Project {new_project} already exists, we will use it")
    bd.projects.set_current(new_project)

else:
    bd.projects.set_current(base_project)
    bd.projects.copy_project(new_project)
    print(f"Created new project {new_project} from {base_project}")

bd.databases

# Get the premise key
key_path = Path(__file__).parents[2] / ".secrets" / "premise_key.txt"
with open(key_path, "r") as f:
    premise_key = f.read()


pm.clear_cache()

# Create new databases for selected future scenarios
# Details of the scenarios can be found here:
# https://www.carbonbrief.org/explainer-how-shared-socioeconomic-pathways-explore-future-climate-change/

ndb = pm.NewDatabase(
    scenarios=[
        {"model": "remind", "pathway": "SSP1-Base", "year": 2050},
        {"model": "remind", "pathway": "SSP2-Base", "year": 2050},
        {"model": "remind", "pathway": "SSP5-Base", "year": 2050},
        {"model": "remind", "pathway": "SSP2-NPi", "year": 2050},
        {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2050},
        {"model": "remind", "pathway": "SSP1-Base", "year": 2040},
        {"model": "remind", "pathway": "SSP2-Base", "year": 2040},
        {"model": "remind", "pathway": "SSP5-Base", "year": 2040},
        {"model": "remind", "pathway": "SSP2-NPi", "year": 2040},
        {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2040},
        {"model":"remind", "pathway":"SSP1-Base", "year":2030},
        {"model":"remind", "pathway":"SSP2-Base", "year":2030},
        {"model":"remind", "pathway":"SSP5-Base", "year":2030},
        {"model":"remind", "pathway":"SSP2-NPi", "year":2030},
        {"model":"remind", "pathway":"SSP2-PkBudg500", "year":2030},
        {"model": "remind", "pathway": "SSP1-Base", "year": 2020},
        {"model": "remind", "pathway": "SSP2-Base", "year": 2020},
        {"model": "remind", "pathway": "SSP5-Base", "year": 2020},
        {"model": "remind", "pathway": "SSP2-NPi", "year": 2020},
        {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2020},
    ],
    source_db="ecoinvent_3.9.1_cutoff",
    source_version="3.9.1",
    # system_model="consequential",
    # system_model_args=args # Optional. Arguments.
    key=premise_key,
)



ndb.update_all()
ndb.update_cars()
ndb.update_buses()
# ndb.update_two_wheelers() # not working
ndb.write_db_to_brightway()
add_premise_gwp()
