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

# ============================================================
# ------------------------------------------------------------
## SETTINGS FOR BRIGHTWAY2

# you can set the brightway2 directory here, otherwise it will use the default one
# custom_bw2_dir = os.path.expanduser("~") + '/brightway2data'
custom_bw2_dir = None
if custom_bw2_dir:
    os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir

import bw2data as bd

# ------------------------------------------------------------
## SETTINGS FOR PROJECTS
# set project name and other things here

project_premise_base = "default"
project_premise = "SSP-cutoff"
project_base = project_premise
# if you want to use the same project for the wmf tool, change this to project_base, otherwise, it will create a new project
project_wmf = f"WMFootprint-{project_base}"

# ------------------------------------------------------------
## SETTINGS FOR THE WASTEANDMATERIAL FOOTPRINT TOOL
use_wmf = False
db_wmf_name = "WasteAndMaterialFootprint"  # name of the database that will be created (pseudobiosphere)

# if you only want to run one database, set single to True and choose the database name here
single = False
single_database = "ecoinvent_cutoff_3.9_remind_SSP5-Base_2050"

# if you want to use a fresh project
delete_wmf_project = False
use_multiprocessing = False
verbose = False

# set these to True if you want to run the different parts of the tool separately
do_search = True
do_methods = True
do_edit = True

# ------------------------------------------------------------
## PREMISE SETTINGS -  to construct future LCA databases with premise

use_premise = False

# this will be the database that premise will use to construct the future databases
database_name = "ecoinvent-3.9.1-cutoff"

# if you want to use a fresh project
delete_existing_premise_project = False

# if you want to use multiprocessing (some people have reported problems with this)
use_mp = True

# if you want to give premise multiple databases at once, increase this number, otherwise, leave it at 1. From my experience, it is better to give it one database at a time, otherwise memory issues can occur.
batch_size = 1

# This seems not to have much effect, because most of the print statemenents are in `wurst`, not in `premise`
premise_quiet = True

if use_premise and project_base != project_premise:
    project_wmf = f"WMFootprint-{project_premise}"

# Get the premise key (at the moment, it is stored in the code to make it easier for people, but it would be better to have it in a file)
premise_key = "tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo="
if premise_key is None:
    key_path = Path(__file__).parents[1] / ".secrets" / "premise_key.txt"
    with open(key_path, "r") as f:
        premise_key = f.read()


# ************************************************************
##  CHOOSE THE SCENARIOS YOU WANT TO USE WITH PREMISE

# Details of the scenarios can be found here:
# carbonbrief.org/explainer-how-shared-socioeconomic-pathways-explore-future-climate-change/
# https://premise.readthedocs.io/en/latest/
# https://premisedash-6f5a0259c487.herokuapp.com/ (there is a nice dashboard here to explore the scenarios)


# Comment out the scenarios you don't want to use, otherwise all potential scenarios will be attempted
# The full list of available scenarios is in the `filenames` variable (at the moment there are 15, but there could be more in future updates)
# Not all combinations are available, the code in FutureScenarios.py will filter out the scenarios that are not possible

models = [
    # "image",
    "remind",
]

ssps = [
    # "SSP1",
    "SSP2",
    # "SSP5",
]

# default is to have an optimistic and a pessimistic scenario
rcps = [
    "Base",
    # "RCP19",
    # "RCP26",
    # "NPi",
    # "NDC",
    "PkBudg500",
    # "PkBudg1150",
]

# If the years you put here are inside the range of the scenario, it will interpolate the data, otherwise, probably it fails. Most of the scenarios are between 2020 and 2100, I think. 5 year intervals until 2050, then 10 year intervals until 2100.

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

# this part makes all the possible combinations of the scenarios you want to use, the will be filtered out later if they are not possible

desired_scenarios = []
for model, ssp, rcp in product(models, ssps, rcps):
    desired_scenarios.append({"model": model, "pathway": ssp + "-" + rcp})


# Set the arguments list of projects and databases to be processed with the WMF tool
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
            db_wmf_name,  # this is the database that will be created by the wmf tool
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


# ------------------------------------------------------------
## GENERAL DIRECTORY PATHS
# Set the paths (to the data, config, logs, and the results)
# By default, the program will create new directories in the working directory


# Get the directory of the main script
cwd = Path.cwd()
# Set the paths
dir_config = cwd / "config"

list_materials = dir_config / "list_materials.txt"

dir_data = cwd / "data"

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

# this will delete old results and logs
if delete_wmf_project:
    for dir in dir_wmf:
        if os.path.exists(dir):
            shutil.rmtree(dir)


# FIN #
# ============================================================
