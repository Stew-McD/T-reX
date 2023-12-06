
'''
|===============================================================|
| File: user_settings.py                                        |
| Project: WasteAndMaterialFooprint                             |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFooprint  |
| Description: Configure Project and Database Settings          |
|---------------------------------------------------------------|
| File Created: Tuesday, 19th September 2023 10:08:47 am        |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                              |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Friday, 29th September 2023 9:15:39 am         |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|


This script is used to configure the project and database settings, as well as set up the essential paths for the data, config, and result directories.

The script allows for two modes of operation for the WasteAndMaterialFootprint tool:

1. Single Mode (`SINGLE` is True):
    - In this mode, the project and database names are set to a single specified value.
    - An argument dictionary containing various project and database names is created and appended to the `args_list`.

2. Multiple projects/databases mode (`MULTIPLE` is True):
    - This mode facilitates batch processing of multiple projects and databases..
    - For each combination of models and versions, an argument dictionary is created and appended to the `args_list`.

After setting the project and database names, the script proceeds to set up various paths using Python's `pathlib` module:

'''

import os
import shutil
from pathlib import Path

# custom_bw2_dir = os.path.expanduser("~") + '/brightway2data'
custom_bw2_dir = None
if custom_bw2_dir:
    os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir

import bw2data as bd

## SETTINGS FOR THE WASTEANDMATERIAL FOOTPRINT TOOL
# set project name and other things here (or give as an argument to main.py)
use_wmf = True
project_base = 'SSP-base_cutoff'
project_wmf = f"WMF-{project_base}"
db_wmf_name = "WasteAndMaterialFootprint"
single = False
database = None
delete = True
use_multiprocessing = False
verbose = False

#%% PREMISE SETTINGS -  to construct future LCA databases

use_premise = False

premise_key = None
project_premise_base = "default"
project_premise = "SSP-base_cutoff"
database_name = "ecoinvent_3.9.1_cutoff"
delete_existing = False
use_mp = False
batch_size = 3

if use_premise:
    project_wmf = f"WMF-{project_premise}"
    
# Get the premise key
if premise_key is None:
    key_path = Path(__file__).parents[1] / ".secrets" / "premise_key.txt"
    with open(key_path, "r") as f:
        premise_key = f.read()

        
# Details of the scenarios can be found here:
# carbonbrief.org/explainer-how-shared-socioeconomic-pathways-explore-future-climate-change/

scenarios_all = [
        {"model": "remind", "pathway": "SSP1-Base", "year": 2050},
        {"model": "remind", "pathway": "SSP1-Base", "year": 2040},
        {"model":"remind", "pathway":"SSP1-Base", "year":2030},
        # {"model": "remind", "pathway": "SSP1-Base", "year": 2020},
        {"model": "remind", "pathway": "SSP2-Base", "year": 2050},
        {"model": "remind", "pathway": "SSP2-Base", "year": 2040},
        {"model":"remind", "pathway":"SSP2-Base", "year":2030},
        # # {"model": "remind", "pathway": "SSP2-Base", "year": 2020},
        # {"model": "remind", "pathway": "SSP2-NPi", "year": 2050},
        # {"model": "remind", "pathway": "SSP2-NPi", "year": 2040},
        # {"model":"remind", "pathway":"SSP2-NPi", "year":2030},
        # # {"model": "remind", "pathway": "SSP2-NPi", "year": 2020},
        # {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2050},
        # {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2040},
        # {"model":"remind", "pathway":"SSP2-PkBudg500", "year":2030},
        # {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2020},
        {"model": "remind", "pathway": "SSP5-Base", "year": 2050},
        {"model": "remind", "pathway": "SSP5-Base", "year": 2040},
        {"model":"remind", "pathway":"SSP5-Base", "year":2030},
        # {"model": "remind", "pathway": "SSP5-Base", "year": 2020},
]

def generate_args_list():
    # change to fit your needs
    bd.projects.set_current(project_base)
    if single:
        databases = [database]
    
    else:
        exclude = ['biosphere3', 'WasteAndMaterialFootprint', 'ecoinvent_3.9.1_consequential']
        databases = sorted([x for x in bd.databases if not any(sub in x for sub in exclude)])
            
    args_list = []
    for database in databases:
        args = {
            "project_base": project_base,
            "project_wmf": project_wmf,
            "db_name": database,
            "db_wmf_name": db_wmf_name,
        }
        args_list.append(args)
        
    return args_list
# %% GENERAL DIRECTORY PATHS
# Set the paths (to the data, config, logs, and the results)

# Get the directory of the main script
cwd = Path.cwd()
# Get the path two levels up
root = cwd.parents[1]

# Set the paths
dir_config = root / "config"
list_materials = dir_config / "list_materials.txt"

dir_data = root / "data"
dir_tmp = dir_data / "tmp"
dir_logs = dir_data / "logs"

dir_searchwaste_results = dir_data / "SearchWasteResults"
dir_searchmaterial_results = dir_data / "SearchMaterialResults"
dir_databases_wasteandmaterial = dir_data / "DatabasesWasteAndMaterial"


dir_wmf = [dir_tmp, dir_logs, dir_searchwaste_results, dir_searchmaterial_results, dir_databases_wasteandmaterial]

if delete:
    for dir in dir_wmf:
        if os.path.exists(dir):
            shutil.rmtree(dir)
