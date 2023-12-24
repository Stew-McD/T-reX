"""
main Module
===========

Main module of the `WasteAndMaterialFootprint` tool.

This script serves as the entry point for the `WasteAndMaterialFootprint` tool. It orchestrates the overall process, including the setup and execution of various subprocesses like database explosion, material and waste searches, and the editing of exchanges. 

The script supports both single and multiple project/database modes, as well as the option to use multiprocessing. It also facilitates the use of the premise module to generate future scenario databases.

Customisation:
--------------
- Project and database names, and other settings can be edited in `config/user_settings.py`.
- Waste search query terms can be customised in `config/queries_waste.py`.
- The list of materials can be modified in `config/queries_materials.py`.

Usage:
------
To use the default settings, run the script with `python main.py`. 
Arguments can be provided to change project/database names or to delete the project before running.

"""

print(
    f"""
    {80*'='}
    {80*'~'}
    {'** Starting the WasteAndMaterialFootprint tool **'.center(80, ' ')}
    {80*'~'}
    {80*'='}
    """
)

# %%  0. Imports and configuration

# Import standard modules
import os
import sys
from time import sleep
from datetime import datetime
from multiprocessing import Pool, cpu_count
from pathlib import Path
import bw2data as bd


# not necessary (but fun), so in a try/except block
try:
    import cowsay
    import logging

    logging.getLogger("playsound").setLevel(logging.ERROR)
    from playsound import playsound
except ImportError:
    pass

# If running on a cluster, get the number of CPUs available
num_cpus = int(
    os.environ.get(
        "SLURM_CPUS_PER_TASK", os.environ.get("SLURM_JOB_CPUS_PER_NODE", cpu_count())
    )
)

# Set the working directory to the location of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the cwd to the Python path
cwd = Path.cwd()
sys.path.insert(0, str(cwd))

# Add the config dir to the Python path
dir_config = cwd.parents[1] / "config"
sys.path.insert(0, str(dir_config))

# import custom modules (from root dir)
from ExchangeEditor import ExchangeEditor
from ExplodeDatabase import ExplodeDatabase
from FutureScenarios import FutureScenarios
from MakeCustomDatabase import dbExcel2BW, dbWriteExcel
from MethodEditor import AddMethods
from SearchMaterial import SearchMaterial
from SearchWaste import SearchWaste
from VerifyDatabase import VerifyDatabase

# import configuration from config/user_settings.py
from user_settings import (
    custom_bw2_dir,
    db_wmf_name,
    delete,
    dir_logs,
    dir_tmp,
    generate_args_list,
    project_base,
    project_premise,
    project_wmf,
    use_multiprocessing,
    use_premise,
    use_wmf,
    do_search,
    do_methods,
    do_edit,
    single_database,
)

# Check from the settings if a custom datadir is declared
if custom_bw2_dir:
    os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir


# %% 1. DEFINE MAIN FUNCTION: WasteAndMaterialFootprint()
def main():
    """
    Main function serving as the wrapper for the WasteAndMaterialFootprint tool.

    This function coordinates the various components of the tool, including:
        creating future scenario databases,
        setting up and processing each database for waste and material footprinting,
        and combining results into a custom database.
        adding LCIA methods to the project for each of the waste/material flows.

    The function supports various modes of operation based on the settings in `config/user_settings.py`.
    Specifications for material and waste searches can be customised in `queries_materials.
    """

    # create future scenario databases
    if use_premise:
        FutureScenarios()

    assert use_wmf, "use_wmf is False, so WasteAndMaterialFootprint will not run"

    start_time = datetime.now()
    args_list = generate_args_list(single_database=single_database)
    total_databases = len(args_list)
    all_databases = list(set(bd.databases) - {"biosphere3"})

    print(
        f"\nStarting WasteAndMaterialFootprint for {total_databases}/{len(all_databases)} databases in project {project_base}\n{'-'*50}"
    )
    for arg in args_list:
        print(f"\t{arg['db_name']}")

    # Make new project, delete previous project if you want to start over, or use existing project
    bd.projects.purge_deleted_directories()
    if project_wmf in bd.projects and delete:
        print(f"\n* Deleting previous project {project_wmf}")
        bd.projects.delete_project(project_wmf, True)
        bd.projects.purge_deleted_directories()

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

    # %% 1.1 Run the initial steps for each database in the project
    def process_db_setup(args, db_number, total_databases):
        """
        Process initial setup for a given database within the project.

        This function is responsible for setting up each database by running the ExplodeAndSearch process.
        It handles any exceptions during the process and logs errors.

        :param dict args: Arguments containing database and project settings.
        :param int db_number: The current database number in the processing sequence.
        :param int total_databases: Total number of databases to be processed.
        :return: int: Returns 1 if successful, 0 if an error occurred.
        """
        print(f'\n{"-"*80}')
        try:
            print(
                f"\n** Pre-processing database ({db_number+1}/{total_databases}): {args['db_name']}**\n"
            )
            print(args)
            if do_search:
                ExplodeAndSearch(args)
            print(f'\n{"-"*80}')
            return 1  # successfully processed
        except Exception as e:
            print(
                f"\n{'@'*50}\n\tError pre-processing database {args['db_name']}! \n\n\t{e}\n{'@'*50}\n"
            )
            print(f'\n{"-"*80}')
            return 0  # error occurred

    results = []
    if use_multiprocessing:
        with Pool(processes=num_cpus) as pool:
            for db_number, arg in enumerate(args_list):
                pool.apply_async(
                    process_db_setup,
                    (arg, db_number, total_databases),
                    callback=results.append,
                )

    else:
        for db_number, arg in enumerate(args_list):
            result = process_db_setup(arg, db_number, total_databases)
            results.append(result)

    successful_count = sum(results)

    end_time = datetime.now()
    duration = end_time - start_time

    if do_methods:
        # %% 1.2 MakeCustomDatabase.py: Make the custom database from the combined search results
        dbWriteExcel()
        dbExcel2BW()
        # %% 1.3 MethodEditor.py: adds LCIA methods to the project for each of the waste/material flows
        AddMethods()

    print(
        f"""
    {80*'-'}
    *** Preprocessing completed ***

    \t Total databases:          {total_databases}
    \t Successfully processed:   {successful_count}
    \t Duration:                 {str(duration).split('.')[0]} (h:m:s)
    {80*'-'}
    
    """
    )

    def process_db(args, db_number, total_databases):
        """
        Process the database by editing exchanges

        :param dict args: Arguments containing database and project settings.
        :param int db_number: The current database number in the processing sequence.
        :param int total_databases: Total number of databases to be processed.

        :return: int: Returns 1 if successful, 0 if an error occurred.
        """
        print(f'\n{"-"*80}')
        try:
            print(
                f"\n** Processing database ({db_number}/{total_databases}): {args['db_name']}**"
            )
            print("Arguments:")
            print(args)
            if do_edit:
                EditExchanges(args)
            print(f'{"-"*80}\n')
            return 1  # successfully processed
        except Exception as e:
            print(
                f"\n{'@'*50}\n\tError processing database {args['db_name']}! \n\n\t{e}\n{'@'*50}\n"
            )
            print(f'{"-"*80}\n')
            return 0  # error occurred

    results = []
    db_number = 0
    if use_multiprocessing:
        with Pool(processes=num_cpus) as pool:
            for arg in args_list:
                pool.apply_async(
                    process_db,
                    (arg, db_number, total_databases),
                    callback=results.append,
                )

    else:
        for args in args_list:
            db_number += 1
            result = process_db(args, db_number, total_databases)
            results.append(result)

    successful_count = sum(results)

    end_time = datetime.now()
    duration = end_time - start_time

    # %% 1.4 VerifyDatabase.py: Verify the database
    print(f'\n{"-"*80}')
    print("\t*** Verifying all databases in the project **")
    for arg in args_list:
        db_name = arg["db_name"]
        VerifyDatabase(project_wmf, db_name)
        print(f'\n{"-"*80}\n')

    try:
        playsound(cwd.parents[1] / "misc/success.mp3")
    except:
        pass

    print(
        f"""
    {80 * '~'}
    {80 * '='}
    {'WasteAndMaterialFootprint Completed'.center(80, ' ')}
    {'~' * 80}

    Project:                  {project_wmf}
    Total Databases:          {total_databases}
    Successfully Processed:   {successful_count}
    Duration:                 {str(duration).split('.')[0]} (h:m:s)

    {'=' * 80}
    {'~' * 80}
    """
    )

    sleep(1)

    try:

        def animate_cowsay(message, delay=0.2):
            cow = cowsay.get_output_string("cow", message)
            for line in cow.split("\n"):
                print(line.center(80, " "))
                sleep(delay)
            playsound(cwd.parents[1] / "misc/moo.mp3")

        message = "\nLet's moooooo\n some LCA!\n"
        animate_cowsay(message)
    except:
        pass

    print(f'\n{"-"*80}\n')
    print(f'\n{"~"*80}\n')
    print(f'\n{"="*80}\n')


def ExplodeAndSearch(args):
    """
    Exploding the database into separate exchanges, searching for waste and
    material flows, and processing these results.

    This includes:
        - ExplodeDatabase.py
        - SearchWaste.py
        - SearchMaterial.py

    :param args: Dictionary containing database and project settings.
    :returns: None
    """

    project_wmf = args["project_wmf"]
    db_name = args["db_name"]

    print(
        f"\n{'='*100}\n\t Starting WasteAndMaterialFootprint for {db_name}\n{'='*100}"
    )

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

    return None


def EditExchanges(args):
    """
    Edit exchanges in the database.

    This function adds waste and material flows to the activities and verifies the database.

    :param args: Dictionary containing database and project settings.
    :returns: None
    """

    db_name = args["db_name"]
    start = datetime.now()
    # Add waste and material flows to the activities, check that it worked

    ExchangeEditor(project_wmf, db_name, db_wmf_name)
    exit_code = VerifyDatabase(project_wmf, db_name)

    if exit_code == 0:
        print("** Database verified successfully! **\n")
    else:
        print("** Error occurred during verification! **")
        print(f"\t Look in the logfile for details. exit_code = {exit_code}\n")

    # Final message and log
    duration = datetime.now() - start
    print(f"{'='*90}")
    print(
        f"\t*** Finished WasteAndMaterialFootprint for {db_name} ***\n\t\t\tDuration: {str(duration).split('.')[0]} (h:m:s)"
    )
    print("\t*** Woah woah wee waa, great success!! ***")
    print(f"{'='*90}")

    with open(f"{dir_logs / 'main_log.txt'}", "a") as log:
        log.write(
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
    main()
