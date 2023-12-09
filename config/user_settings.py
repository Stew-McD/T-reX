"""
user_settings Module
====================

Configure Project and Database Settings for WasteAndMaterialFootprint tool.

This script is used to configure the project and database settings, as well as set up the essential paths for the data, config, and result directories.

The script allows for two modes of operation:
    1. Single Mode (`single` is True): Set the project and database names to a single specified value.
    2. Multiple projects/databases mode (`single` is False): Facilitates batch processing of multiple projects and databases.

Additionally, the script allows for the use of multiprocessing (`use_multiprocessing` is True). 

Premise can also be used to make future databases (`use_premise` is True).


Author: Stewart Charles McDowall
Email: s.c.mcdowall@cml.leidenuniv.nl
GitHub: Stew-McD
Institution: CML, Leiden University
Licence: The Unlicense

"""

import os
import shutil
from pathlib import Path

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
project_base = "SSP-cutoff"
project_wmf = f"WMFootprint-{project_base}"
db_wmf_name = "WasteAndMaterialFootprint"
single = False
database = None
delete = True
use_multiprocessing = False
verbose = False

# %% PREMISE SETTINGS -  to construct future LCA databases

use_premise = True

premise_key = None  # add your own key here or have it stored in .secrets/premise_key.txt (tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=)
project_premise_base = "default"
project_premise = project_base
database_name = "ecoinvent_3.9.1_cutoff"
delete_existing = True
use_mp = False
batch_size = 3
premise_quiet = True

if use_premise:
    project_wmf = f"WMFootprint-{project_premise}"

# Get the premise key
if premise_key is None:
    key_path = Path(__file__).parents[1] / ".secrets" / "premise_key.txt"
    with open(key_path, "r") as f:
        premise_key = f.read()


# Choose the scenarios to be processed with premise
# Details of the scenarios can be found here:
# carbonbrief.org/explainer-how-shared-socioeconomic-pathways-explore-future-climate-change/
# https://premise.readthedocs.io/en/latest/
# https://premisedash-6f5a0259c487.herokuapp.com/ (there is a nice dashboard here to explore the scenarios)
scenarios_all = [
    {"model": "remind", "pathway": "SSP1-Base", "year": 2050},
    {"model": "remind", "pathway": "SSP1-Base", "year": 2040},
    {"model": "remind", "pathway": "SSP1-Base", "year": 2030},
    {"model": "remind", "pathway": "SSP1-Base", "year": 2020},
    {"model": "remind", "pathway": "SSP2-Base", "year": 2050},
    {"model": "remind", "pathway": "SSP2-Base", "year": 2040},
    {"model": "remind", "pathway": "SSP2-Base", "year": 2030},
    {"model": "remind", "pathway": "SSP2-Base", "year": 2020},
    {"model": "remind", "pathway": "SSP5-Base", "year": 2050},
    {"model": "remind", "pathway": "SSP5-Base", "year": 2040},
    {"model": "remind", "pathway": "SSP5-Base", "year": 2030},
    {"model": "remind", "pathway": "SSP5-Base", "year": 2020},
    {"model": "remind", "pathway": "SSP1-PkBudg500", "year": 2050},
    {"model": "remind", "pathway": "SSP1-PkBudg500", "year": 2040},
    {"model": "remind", "pathway": "SSP1-PkBudg500", "year": 2030},
    {"model": "remind", "pathway": "SSP1-PkBudg500", "year": 2020},
    {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2050},
    {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2040},
    {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2030},
    {"model": "remind", "pathway": "SSP2-PkBudg500", "year": 2020},
    {"model": "remind", "pathway": "SSP5-PkBudg500", "year": 2050},
    {"model": "remind", "pathway": "SSP5-PkBudg500", "year": 2040},
    {"model": "remind", "pathway": "SSP5-PkBudg500", "year": 2030},
    {"model": "remind", "pathway": "SSP5-PkBudg500", "year": 2020},
]

# Set the project and databases to be processed with the WMF tool
def generate_args_list():
    """
    Generate a list of argument dictionaries for processing multiple projects and databases.

    This function is used when the tool is set to operate in multiple projects/databases mode.
    It generates a list of argument dictionaries, each containing project and database settings.

    :returns: A list of dictionaries with project and database settings for batch processing.
    """
    bd.projects.set_current(project_base)
    if single:
        databases = [database]

    else:
        exclude = [
            "biosphere",
            "WasteAndMaterialFootprint",
        ]
        databases = sorted(
            [x for x in bd.databases if not any(sub in x for sub in exclude)]
        )

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


dir_wmf = [
    dir_tmp,
    dir_logs,
    dir_searchwaste_results,
    dir_searchmaterial_results,
    dir_databases_wasteandmaterial,
]

if delete:
    for dir in dir_wmf:
        if os.path.exists(dir):
            shutil.rmtree(dir)
