#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
|===============================================================|
| File: FutureScenariosConsequential.py                         |
| Project: WasteAndMaterialFootprint                            |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint |
| Description: <<description>>                                  |
|---------------------------------------------------------------|
| File Created: Friday, 22nd September 2023 11:51:18 am         |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                              |
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

import os
import sys
import logging
from pathlib import Path
from itertools import zip_longest

import bw2data as bd
import premise as pm
from premise_gwp import add_premise_gwp


# change working directory to the location of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# set the project directory if you want
# os.environ["BRIGHTWAY2_DIR"] = os.path.expanduser("~") + '/bw'

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
file_handler = logging.FileHandler('../../data/logs/FutureScenarios.log')
file_handler.setLevel(logging.INFO)

# create a stream handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info('*** Starting FutureScenariosConsequential.py ***')

# function to split a list into chunks of n (to avoid memory errors)
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

# Make a new project
base_project = "default"
new_project = "SSP125_con"
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

# Get the premise key
key_path = Path(__file__).parents[2] / ".secrets" / "premise_key.txt"
with open(key_path, "r") as f:
    premise_key = f.read()

if delete_existing: 
    pm.clear_cache()

# Create new databases for selected future scenarios
# Details of the scenarios can be found here:
# https://www.carbonbrief.org/explainer-how-shared-socioeconomic-pathways-explore-future-climate-change/

scenarios_all = [
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
]

batch_size = 5
count = 0
for scenarios_set in grouper(scenarios_all, batch_size):
    
    # information on the scenarios being processed
    count += 1
    logging.info(f'\n ** Processing scenario set \
        {count} of{len(scenarios_all)/batch_size : .0f}')
    for scenario in scenarios_set:
        logging.info(f'    - {scenario["model"]}, \
                     {scenario["pathway"]}, \
                     {scenario["year"]}')
    
    # premise functions
    ndb = pm.NewDatabase(
        scenarios= scenarios_set,
        source_db="ecoinvent_3.9.1_consequential",
        source_version="3.9.1",
        system_model="consequential",
        # system_model_args=args # Optional. Arguments.
        key=premise_key,
    )

    ndb.update_all()
    # ndb.update_cars()
    # ndb.update_buses()
    # ndb.update_two_wheelers() # not working
    ndb.write_db_to_brightway()

# add biogenic carbon, etc. to the project
add_premise_gwp()


logging.info("Done!")
