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


"""

import os
import shutil
from itertools import product
from pathlib import Path

from WasteAndMaterialFootprint import CUSTOM_CONFIG_DIR, CUSTOM_DATA_DIR, CUSTOM_LOG_DIR


# custom_bw2_dir = os.path.expanduser("~") + '/brightway2data'
custom_bw2_dir = None
if custom_bw2_dir:
    os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir

import bw2data as bd

## SETTINGS FOR PROJECTS
project_premise_base = "default"
project_premise = "SSP-cutoff"
project_base = project_premise
project_wmf = f"WMFootprint-{project_base}"


## SETTINGS FOR THE WASTEANDMATERIAL FOOTPRINT TOOL
# set project name and other things here (or give as an argument to main.py)
use_wmf = False
# if you want to use the same project for the wmf tool, change this to project_base, otherwise, it will create a new project
db_wmf_name = "WasteAndMaterialFootprint"
single = False
single_database = "ecoinvent_cutoff_3.9_remind_SSP5-Base_2050"  # choose one here
delete = True
use_multiprocessing = False
verbose = False
do_search = True
do_methods = True
do_edit = True

# %% PREMISE SETTINGS -  to construct future LCA databases
# only databases that do not exist will be created

use_premise = False
premise_key = "tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo="
database_name = "ecoinvent-3.9.1-cutoff"
delete_existing = False
use_mp = True
batch_size = 1
premise_quiet = True

if use_premise and project_base != project_premise:
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


# CHOOSE SCENARIOS
# Comment out the scenarios you don't want to use, otherwise all potential scenarios will be attempted
# The full list of available scenarios is in the `filenames` variable (atm 15, but there could be more in future updates)
# Not all combinations are available, later, we will filter out the scenarios that are not possible

models = [
    # "image",
    "remind",
]

ssps = [
    # "SSP1",
    "SSP2",
    # "SSP5",
]

rcps = [
    "Base",  # choose the rcp you want to use, (mostly this comment is to stop the linter from removing the line breaks)
    # "RCP19",
    # "RCP26",
    # "NPi",
    # "NDC",
    "PkBudg500",
    # "PkBudg1150",
]

# If the years you put here are inside the range of the scenario, in will interpolate the data, otherwise, probably it fails. Most of the scenarios are between 2020 and 2100, I think.

years = [
    # 2020,
    # 2025,
    2030,
    # 2035,
    # 2040,
    # 2045,
    # 2050,
    # 2060,
    2065,
    # 2070,
    # 2080,
    # 2090,
    2100,
]

# this part makes all the possible combinations of the scenarios you want to use, the next part will filter out the ones that are not available

desired_scenarios = []
for model, ssp, rcp in product(models, ssps, rcps):
    desired_scenarios.append({"model": model, "pathway": ssp + "-" + rcp})


# Set the project and databases to be processed with the WMF tool
def generate_args_list(single_database=None):
    """
    Generate a list of argument dictionaries for processing multiple projects and databases.

    This function is used when the tool is set to operate in multiple projects/databases mode.
    It generates a list of argument dictionaries, each containing project and database settings.

    :returns: A list of dictionaries with project and database settings for batch processing.
    """
    bd.projects.set_current(project_base)
    if single:
        databases = [single_database]

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
cwd = Path(__file__).resolve().parents[0]
# Get the path two levels up
root = cwd.parents[0]

# Set the paths
if CUSTOM_CONFIG_DIR.is_dir():
    dir_config = CUSTOM_CONFIG_DIR
else:
    dir_config = root / "config"

list_materials = dir_config / "list_materials.txt"

if not CUSTOM_DATA_DIR.is_dir():
    CUSTOM_DATA_DIR.mkdir(parents=True, exist_ok=True)
dir_data = CUSTOM_DATA_DIR
# dir_data = root / "data"

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
