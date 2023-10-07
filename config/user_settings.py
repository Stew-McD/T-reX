#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

The script allows for two modes of operation:

1. Single Mode (`SINGLE` is True):
    - In this mode, the project and database names are set to a single specified value.
    - An argument dictionary containing various project and database names is created and appended to the `args_list`.

2. Multiple projects/databases mode (`MULTIPLE` is True):
    - This mode facilitates batch processing of multiple projects and databases..
    - For each combination of models and versions, an argument dictionary is created and appended to the `args_list`.

After setting the project and database names, the script proceeds to set up various paths using Python's `pathlib` module:

'''

import os
from pathlib import Path

custom_bw2_dir = os.path.expanduser("~") + '/brightway2data'
if custom_bw2_dir:
    os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir

import bw2data as bd

project_base = 'default'
project_wmf = f"WMF-{project_base}"
db_wmf_name = "WasteAndMaterialFootprint"
single = False
database = None
delete = True
use_multiprocessing = False

# set project name and other things here (or give as an argument to main.py)
def generate_args_list():
    # change to fit your needs
    bd.projects.set_current(project_base)
    if single:
        databases = [database]
    
    else:
        exclude = ['biosphere3', 'WasteAndMaterialFootprint']
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


# %% DIRECTORY PATHS
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
