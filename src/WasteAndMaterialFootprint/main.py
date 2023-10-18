'''
|===============================================================|
| File: main.py                                                 |
| Project: WasteAndMaterialFootprint                            |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint |
| Description: Main module of `WasteAndMaterialFootprint` tool  |
|---------------------------------------------------------------|
| File Created: Monday, 18th September 2023 11:21:13 am         |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                              |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Monday, 16th October 2023 5:27:34 pm           |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|

* To use the ``default`` settings, simply run the whole script using "python main.py".

* You can provide arguments to the script to change the project and database names, 
and to delete the project before running.

* You can customize the terms of the waste search query in config/queries_waste.py
 and the list of materials in config/default_materials.py.
 
* The other settings, like the names of the projects and databases can be 
 edited in config/user_settings.py.

'''

#%%  0. Imports and configuration

# Import standard modules
import argparse
import os
import sys
from datetime import datetime
from multiprocessing import Pool, cpu_count
from pathlib import Path

# If running on a cluster, get the number of CPUs available
num_cpus = int(
    os.environ.get(
        "SLURM_CPUS_PER_TASK", os.environ.get("SLURM_JOB_CPUS_PER_NODE", cpu_count())
    )
)

# Set the working directory to the location of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the root dir to the Python path
cwd = Path.cwd()
sys.path.insert(0, str(cwd))

# Add the config dir to the Python path
dir_config = cwd.parents[1] / "config"
sys.path.insert(0, str(dir_config))

# import custom modules (from root dir)
from ExchangeEditor import ExchangeEditor
from ExplodeDatabase import ExplodeDatabase
from MakeCustomDatabase import dbExcel2BW, dbWriteExcel
from MethodEditor import AddMethods
from SearchMaterial import SearchMaterial
from SearchWaste import SearchWaste
from VerifyDatabase import VerifyDatabase
from FutureScenarios import FutureScenarios

# import configuration from config/user_settings.py
from user_settings import (
    custom_bw2_dir,
    db_wmf_name,
    delete,
    dir_logs,
    dir_tmp,
    generate_args_list,
    project_base,
    project_wmf,
    use_premise,
    use_multiprocessing,
    use_wmf,
)

print(f"{80*'='}")
print(f'\t ** Starting WasteAndMaterialFootprint for project "{project_base}" **')
print(f"{80*'='}")

# Check from the settings if a custom datadir is declared
if custom_bw2_dir:
    os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir
import bw2data as bd

# Run premise to make future scenarios databases



# %% 1. DEFINE MAIN FUNCTION: WasteAndMaterialFootprint()
def main():
    """Main function serving as a wrapper for the WasteAndMaterialFootprint tool."""

    # create future scenario databases
    if use_premise:
        FutureScenarios()
        
    assert use_wmf, "use_wmf is False, so WasteAndMaterialFootprint will not run"
        
    start_time = datetime.now()
    args_list = generate_args_list()
    total_databases = len(args_list)
    all_databases = list(set(bd.databases) - {'biosphere3'})

    print(f"\nStarting WasteAndMaterialFootprint for {total_databases}/{len(all_databases)} databases in project {project_base}\n{'-'*50}")
    for arg in args_list:
        print(f"\t{arg['db_name']}")

    
    # Make new project, delete previous project if you want to start over, or use existing project
    bd.projects.purge_deleted_directories()
    if project_wmf in bd.projects and delete:
        print(f"\n* Deleting previous project {project_wmf}")
        bd.projects.delete_project(project_wmf, True)

    if project_wmf in bd.projects:
        print(f"* WasteAndMaterial project already exists: {project_wmf}")
        bd.projects.set_current(project_wmf)

    if project_wmf not in bd.projects:
        print(
            f"\n* Project {project_base} will be copied to a new project: {project_wmf}"
        )
        bd.projects.set_current(project_base)
        bd.projects.copy_project(project_wmf)
        bd.projects.set_current(project_wmf)

    #%% 1.1 Run the initial steps for each database in the project
    def process_db_setup(args):
        try:
            print(f"\n* Processing database {args['db_name']}\n")
            print(args)
            ExplodeAndSearch(args)
            return 1  # successfully processed
        except Exception as e:
            print(f"\n{'@'*50}\n\tError processing database {args['db_name']}! \n\n\t{e}\n{'@'*50}\n")
            return 0  # error occurred

    results = []
    if use_multiprocessing:
        with Pool(processes=num_cpus) as pool:
            for arg in args_list:
                pool.apply_async(process_db_setup, (arg,), callback=results.append)

    else:
        for args in args_list:
            result = process_db_setup(args)
            results.append(result)

    successful_count = sum(results)

    end_time = datetime.now()
    duration = end_time - start_time

    print(
        f"""
    *** Processing Completed ***

    \t Total databases:          {total_databases}
    \t Successfully processed:   {successful_count}
    \t Duration:                 {str(duration).split('.')[0]} seconds
    
    """
    )

    # %% 1.2 MakeCustomDatabase.py: Make the custom database from the combined search results
    dbWriteExcel()
    dbExcel2BW()
    # %% 1.3 MethodEditor.py: adds LCIA methods to the project for each of the waste/material flows
    AddMethods()

    def process_db(args):
        ''' This function is called by the multiprocessing pool'''
        try:
            print(f"\n* Processing database {args['db_name']}\n")
            print(args)
            EditExchanges(args)
            return 1  # successfully processed
        except Exception as e:
            print(
                f"\n{'@'*50}\n\tError processing database {args['db_name']}! \n\n\t{e}\n{'@'*50}\n"
            )
            return 0  # error occurred

    results = []
    if use_multiprocessing:
        with Pool(processes=num_cpus) as pool:
            for arg in args_list:
                pool.apply_async(process_db, (arg,), callback=results.append)

    else:
        for args in args_list:
            result = process_db(args)
            results.append(result)

    successful_count = sum(results)

    end_time = datetime.now()
    duration = end_time - start_time

    for arg in args_list:
        db_name = arg["db_name"]
        VerifyDatabase(project_wmf, db_name)

    print(
        f"""
    *** Processing Completed ***

    Total databases:          {total_databases}
    Successfully processed:   {successful_count}
    Duration:                 {str(duration).split('.')[0]} seconds
    """
    )

def ExplodeAndSearch(args):
    """
    This function is called by the multiprocessing pool 
    to run the setup for each database in the project.
        This includes:
            - ExplodeDatabase.py
            - SearchWaste.py
            - SearchMaterial.py
    """

    project_wmf = args["project_wmf"]
    db_name = args["db_name"]

    print(f"\n{'='*80}\n\t Starting WasteAndMaterialFootprint for {db_name}\n{'='*80}")

    # %% 1.2 Explode the database into separate exchanges
    existing_file = dir_tmp / (db_name + "_exploded.pickle")
    if os.path.isfile(existing_file):
        print(f"\n* Existing exploded database found: {existing_file}")
        print("\n* Existing data will be reused for the current run")
    else:
        ExplodeDatabase(db_name)

    # %% 1.3 Search the exploded database for waste and material flows
    SearchWaste(db_name)
    SearchMaterial(db_name, project_wmf)

    return

def EditExchanges(args):
    db_name = args["db_name"]
    start = datetime.now()
    # Add waste and material flows to the activities, check that it worked
    
    ExchangeEditor(project_wmf, db_name, db_wmf_name)
    exit_code = VerifyDatabase(project_wmf, db_name)
    
    if exit_code == 0:
        print("** Database verified successfully! **")
    else:
        print("** Error occurred during verification! **")
        print(f"\t Look in the logfile for details. exit_code = {exit_code}")

    # Final message and log
    duration = datetime.now() - start
    print(f"{'='*50}")
    print(
        f"\n*** Finished WasteAndMaterialFootprint.\n\tDuration: {str(duration).split('.')[0]} ***"
    )
    print("\t** Woah woah wee waa, great success!! **")
    print(f"{'='*50}")

    with open(f"{dir_logs / 'main_log.txt'}", "a") as l:
        l.write(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + "\t Duration:"
            + str(duration).split(".")[0]
            + " "
            + db_name
            + "\n"
        )

    return


# %% 2. RUN MAIN FUNCTION
if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="CLI for your project.")
    # parser.add_argument("--project", type=str, default="default", help='Project name. Default is "default".')
    # parser.add_argument("--single", action="store_true", help="Use a single databases. Default is False.")
    # parser.add_argument("--database", type=str, default="ecoinvent_3.9.1_cutoff", help='Database name. Default:"ecoinvent_3.9.1_cutoff".')
    # parser.add_argument("--delete", action="store_true", help="Delete the old project before running. Default is False.")
    # parser.add_argument("--multiprocessing", action="store_true", help="Use multiprocessing. Default is False.")
    # parser.add_argument("--use_premise", action="store_true", help="Use premise to make future scenarios databases. Default is False.")
    # args_cli = parser.parse_args()

    # main(
    #     custom_bw2_dir, 
    #      project=args_cli.project, 
    #      single=args_cli.single, 
    #      database=args_cli.database, 
    #      delete_project=args_cli.delete, 
    #      use_multiprocessing=args_cli.multiprocessing, 
    #      use_premise=args_cli.use_premise
    #      )
    
    main()
