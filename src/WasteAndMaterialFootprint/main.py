#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
``WasteAndMaterialFootprint``

This is the main module of the ``WasteAndMaterialFootprint`` tool, designed to analyze waste and material footprints in life cycle assessments.

To use the ``default`` settings, simply run the whole script using "python main.py".
You can customize the terms of the waste search query in config/queries_waste.py
and the list of materials in config/list_materials.txt.
The names of the projects and databases can be edited in config/user_settings.py.

``DEFAULTS``:
EI database named in the form ``default_<db_name>``.

The script will copy the project ``default_``+<db_name> to a new project:
- 'project_base': ``default_``+<dbase>,
- 'project_wasteandmaterial': ``WasteAndMaterialFootprint_``+<dbase>.

Created on Sat Nov 19 11:24:06 2022
@author: Stew-McD
Based on the work of LL
"""

# %%  0. Imports and configuration

# import standard modules
import os
import sys
from pathlib import Path
from datetime import datetime
import bw2data as bd
from multiprocessing import Pool, cpu_count
import argparse
from time import sleep

num_cpus = int(os.environ.get('SLURM_CPUS_PER_TASK', os.environ.get('SLURM_JOB_CPUS_PER_NODE', cpu_count())))

# Set the working directory to the location of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the root dir to the Python path
cwd = Path.cwd()
sys.path.insert(0, str(cwd))

# Add the config dir to the Python path
dir_config = cwd.parents[1] / "config"
sys.path.insert(0, str(dir_config))


# run premise first
# import FutureScenariosConsequential 

# import custom modules (from root dir)
from ExplodeDatabase import ExplodeDatabase
from SearchWaste import SearchWaste
from SearchMaterial import SearchMaterial
from MakeCustomDatabase import dbWriteExcel, dbExcel2BW
from MethodEditor import AddMethods
from ExchangeEditor import ExchangeEditor

# import configuration from config/user_settings.py
from user_settings import dir_tmp, dir_logs, generate_args_list

# %% 1. DEFINE MAIN FUNCTION: WasteAndMaterialFootprint()

def WasteAndMaterialFootprint(args):
    db_name = args["db_name"]
    db_wasteandmaterial_name = args["db_wasteandmaterial_name"]
    print(f"\n{'='*80}\n\t Starting WasteAndMaterialFootprint for {db_name}\n{'='*80}")
    start = datetime.now()

    # %% 1.2 Explode the database into separate exchanges
    # ExplodeDatabase.py
    # Open up EcoInvent db with wurst and save results as .pickle (also delete files from previous runs if you want)
    existing_file = dir_tmp / (db_name + "_exploded.pickle")
    if os.path.isfile(existing_file):
        print(f"\n* Existing exploded database found: {existing_file}")
        print("\n* Existing data will be reused for the current run")
    else:
        ExplodeDatabase(db_name)

    # %% 1.3 Search the exploded database for waste and material flows
    # 1.3.1 SearchWaste.py
    # run SearchWaste() for the list of waste queries defined in config/queries_waste.py
    SearchWaste(db_name)
    # 1.3.2 SearchMaterial.py
    # run SearchMaterial for the list of materials defined in config/list_materials.txt
    # or from the default list in config/default_materials.py
    SearchMaterial(db_name, project_wasteandmaterial)

    # %% 1.4 Make the custom database from search results
    # 1.4.1 MakeCustomDatabase.py
    # From the SearchWaste() and SearchMaterial() results make an xlsx file in the database format needed for brightway2
    dbWriteExcel(db_name, db_wasteandmaterial_name)
    # imports the custom database "db_wasteandmaterial_<db_name>" to the brightway project "WasteAndMaterialFootprint_<db_name>"
    dbExcel2BW(project_wasteandmaterial, db_wasteandmaterial_name)

    # 1.4.2 MethodEditor.py
    # adds LCIA methods to the project for each of the waste and material categories defined in the custom database
    #AddMethods(project_wasteandmaterial, db_wasteandmaterial_name)

    # %% 1.5 Add waste and material flows to the activities
    # ExchangeEditor.py
    # adds waste and material flows as elementary exchanges to each of the activities found by the search functions
    #ExchangeEditor(project_wasteandmaterial, db_name, db_wasteandmaterial_name)

    # %% 1.5 Final message and log
    # print message to console
    duration = datetime.now() - start
    print(f"{'='*50}")
    print(
        f"\n*** Finished running WasteAndMaterialFootprint.\n\tDuration: {str(duration).split('.')[0]} ***"
    )
    print("\t** Woah woah wee waa, great success!! **")
    print(f"{'='*50}")

    # write the details of the run to a log file
    with open(f"{dir_logs / 'main_log.txt'}", "a") as l:
        l.write(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + "\t Duration:"
            + str(duration).split(".")[0]
            + " "
            + db_name
            + "\n"
        )

    return None


# %% 2. RUN MAIN FUNCTION
if __name__ == "__main__":

    start_time = datetime.now()

    parser = argparse.ArgumentParser(description='CLI for your project.')
    parser.add_argument('--project', type=str, default='default', help='Project name. Default is "default".')
    parser.add_argument('--multiple', action='store_true', help='Use multiple databases. Default is False.')
    parser.add_argument('--databases', type=str, nargs='+', default=['ecoinvent_3.9.1_cutoff'], help='List of database names. Default is ["ecoinvent_3.9.1_cutoff"].')
    parser.add_argument('--delete', action='store_true', help='Delete the old project before running. Default is False.')
    parser.add_argument("--multiprocessing", action="store_true", help="Use multiprocessing. Default is False.")
    # Parse the arguments
    args_cli = parser.parse_args()
    delete_project = args_cli.delete
    use_multiprocessing = args_cli.multiprocessing
    args_list = generate_args_list(project=args_cli.project, multiple=args_cli.multiple, databases=args_cli.databases)
    total_databases = len(args_list)
    
    # Set the global vars from the arguments
    project_base = args_list[0]["project_base"]
    project_wasteandmaterial = args_list[0]["project_wasteandmaterial"]

    # %%
    print(
        f"\n\n{'#'*100}\n*** Beginning WasteAndMaterialFootprint for {total_databases} databases  in project '{project_base}***\n"
    )
    for arg in args_list:
        print(f"\t{arg['db_name']}")
    print(f"{'#' * 100}\n\n")
    
    # make new project, delete previous project if you want to start over, or use existing project
    if project_wasteandmaterial in bd.projects:
        print(f"* WasteAndMaterial project already exists: {project_wasteandmaterial}")
        bd.projects.set_current(project_wasteandmaterial)
    
    if project_wasteandmaterial in bd.projects and delete_project:
        print(f"\n* Deleting previous project {project_wasteandmaterial}")
        bd.projects.delete_project(project_wasteandmaterial, delete_dir=True)
    
    if project_wasteandmaterial not in bd.projects:
        print(f"\n* Project {project_base} will be copied to a new project: {project_wasteandmaterial}")
        bd.projects.set_current(project_base)
        bd.projects.copy_project(project_wasteandmaterial)


    def process_db(args):
        try:
            print(f"\n* Processing database {args['db_name']}\n")
            WasteAndMaterialFootprint(args)
            return 1  # successfully processed
        except Exception as e:
            print(f"\n{'@'*50}\n\tError processing database {args['db_name']}! \n\n\t{e}\n{'@'*50}\n")
            return 0  # error occurred
    
    if use_multiprocessing:
        with Pool(processes=num_cpus) as pool:
            results = []
            for arg in args_list:
                pool.apply_async(process_db, (arg,), callback=results.append)
                sleep(5)  # sleep for 5 seconds before sending the next task

            pool.close()
            pool.join()
    else:
        results = [process_db(arg) for arg in args_list]

        successful_count = sum(results)
        error_count = len(results) - successful_count

        end_time = datetime.now()
        duration = end_time - start_time

    print(f"""
    *** Processing Completed ***

    Total databases:          {total_databases}
    Successfully processed:   {successful_count}
    Duration:                 {str(duration).split('.')[0]} seconds
    """)
