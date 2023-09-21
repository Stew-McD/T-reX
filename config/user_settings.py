"""
user_settings.py

Script to Configure Project and Database Settings

-----
Author: SC-McD
Email: s.c.mcdowall@cml.leidenuniv.nl
Created: 2023-09-11
-----

This script is used to configure the project and database settings, as well as set up the essential paths for the data, config, and result directories.

The script allows for two modes of operation:

1. Single Project Mode (`SINGLE_PROJECT` is True):
    - In this mode, the project and database names are set to a single specified value.
    - The `database` variable is used to define the database name.
    - An argument dictionary containing various project and database names is created and appended to the `args_list`.

2. Multiple Projects Mode (`SINGLE_PROJECT` is False):
    - This mode facilitates batch processing of multiple projects sharing a naming convention.
    - Users can specify different versions and models which are then used to create different database names.
    - For each combination of models and versions, an argument dictionary is created and appended to the `args_list`.

After setting the project and database names, the script proceeds to set up various paths using Python's `pathlib` module:

"""
from pathlib import Path

# Set projects and database names
SINGLE_PROJECT = False
database = "cutoff391"

if SINGLE_PROJECT:
    args_list = []
    args = {
        "project_base": "default_" + database,
        "project_wasteandmaterial": "WasteAndMaterialFootprint_" + database,
        "db_name": database,
        "db_wasteandmaterial_name": "db_wasteandmaterial_" + database,
    }
    args_list.append(args)

# if you have a series of projects with a naming convention
# the same as this one, it is easy to run them all in a loop

if not SINGLE_PROJECT:
    versions = ["391"]  # "35", "38","39",
    models = ["con", 'cutoff', 'apos']  # , 'apos','con']
    databases = [f"{x}{y}" for x in models for y in versions]

    args_list = []
    for database in databases:
        args = {
            "project_base": "default_" + database,
            "project_wasteandmaterial": "WasteAndMaterialFootprint_" + database,
            "db_name": database,
            "db_wasteandmaterial_name": "db_wasteandmaterial_" + database,
        }
        args_list.append(args)


# %% Set the paths (to the data, config, and the results

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
