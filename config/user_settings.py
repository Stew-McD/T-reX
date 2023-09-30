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
import bw2data as bd

# os.environ["BRIGHTWAY2_DIR"] = os.path.expanduser("~") + '/bw'

# Set projects and database names
SINGLE = False
MULTIPLE = True

# change to fit your needs
if SINGLE:
    database = "ecoinvent_cutoff_3.9"  # for example
    args_list = []
    args = {
        "project_base": "default_" + database,
        "project_wasteandmaterial": "WMF" + database,
        "db_name": database,
        "db_wasteandmaterial_name": "WMF-" + database,
    }
    args_list.append(args)

if MULTIPLE:
    args_list = []
    
    projects = ["SSP125"]
    for project in projects:
        bd.projects.set_current(project)
        
        databases = None # you could also specify a list of databases here
        
        if not databases:
            exclude = ['biosphere3']
            databases = sorted([x for x in bd.databases if not any(sub in x for sub in exclude)])
            
            # databases.remove('ecoinvent_cutoff_3.9')

        for database in databases:
            args = {
                "project_base": project,
                "project_wasteandmaterial": f"WMF-{project}",
                "db_name": database,
                "db_wasteandmaterial_name": "WMF-" + database,
            }
            args_list.append(args)


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
