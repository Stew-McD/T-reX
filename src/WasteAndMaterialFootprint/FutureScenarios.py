"""
FutureScenarios Module
======================

This module is responsible for creating future databases with premise.


"""

# Imports
import logging
import os
import math
from datetime import datetime
from itertools import zip_longest
from pathlib import Path

import bw2data as bd

# Import user settings or set defaults
try:
    from user_settings import (
        batch_size,
        database_name,
        delete_existing_premise_project,
        dir_data,
        dir_logs,
        premise_key,
        premise_quiet,
        project_premise,
        project_premise_base,
        desired_scenarios,
        use_mp,
        use_premise,
        verbose,
        years,
    )


except ImportError:
    print("No user_settings.py file found, using defaults")
    premise_key = None
    project_premise_base = "default"
    project_premise = "premise_default"
    database_name = "ecoinvent-3.9.1-cutoff"
    delete_existing_premise_project = True
    batch_size = 3
    desired_scenarios = [{"model": "remind", "pathway": "SSP2-Base", "year": 2050}]
    dir_logs = Path.cwd()
    verbose = False
    use_mp = False

if use_premise:
    # easiest way to stop premise from making a mess in the main directory
    dir_premise = dir_data / "premise"
    os.makedirs(dir_premise, exist_ok=True)
    os.chdir(dir_premise)

    import premise as pm
    from premise_gwp import add_premise_gwp

    # Initialize logging with timestamp
    if not os.path.exists(dir_logs):
        os.makedirs(dir_logs)
    log_filename = datetime.today().strftime(f"{dir_logs}/%Y%m%d_FutureScenarios.log")
    logging.basicConfig(filename=log_filename, level=logging.INFO)

    # Function to split scenarios into smaller groups (for batch processing)
    def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    # ---------------------------------------------------------------------------------
    # FILTER OUT SCENARIOS THAT ARE NOT AVAILABLE
    # ---------------------------------------------------------------------------------

    SCENARIO_DIR = pm.filesystem_constants.DATA_DIR / "iam_output_files"
    filenames = sorted([x for x in os.listdir(SCENARIO_DIR) if x.endswith(".csv")])

    # Split the string and extract the version number
    # parts = database_name.split("_")
    # source_version = parts[1] if "." in parts[1] else parts[1].split(".")[0]
    # source_systemmodel = parts[-1]


# function to make arguments for "new database -- pm.nbd" based on possible scenarios
def make_possible_scenario_list(filenames, desired_scenarios, years):
    """
    Make a list of dictionaries with scenario details based on the available scenarios and the desired scenarios.

    args: filenames (list): list of filenames of available scenarios
    desired_scenarios (list): list of dictionaries with scenario details
    years (list): list of years to be used

    returns: scenarios (list): list of dictionaries with scenario details that are available and desired

    """
    possible_scenarios = []
    for filename in filenames:
        climate_model = filename.split("_")[0]
        ssp = filename.split("_")[1].split("-")[0]
        rcp = filename.split("_")[1].split("-")[1].split(".")[0]
        possible_scenarios.append({"model": climate_model, "pathway": ssp + "-" + rcp})

    # scenarios = overlap of desired_scenarios and possible_scenarios
    scenarios = [x for x in desired_scenarios if x in possible_scenarios]

    # now add the years
    scenarios = [{**scenario, "year": year} for scenario in scenarios for year in years]

    return scenarios


def check_existing(desired_scenarios):
    """
    Check the project to see if the desired scenarios already exist, and if so, remove them from the list of scenarios to be created.
    Quite useful when running many scenarios, as it can take a long time to create them all, sometimes crashes, etc.

    args: desired_scenarios (list): list of dictionaries with scenario details

    returns: new_scenarios (list): list of dictionaries with scenario details that do not already exist in the project

    """
    if use_premise:
        bd.projects.set_current(project_premise)
        databases = list(bd.databases)

        db_parts = database_name.split("-")
        version = db_parts[-2]
        model = db_parts[-1]
        if version == "3.9.1":
            version = "3.9"

        new_scenarios = []
        for scenario in desired_scenarios:
            db_name = f"ecoinvent_{model}_{version}_{scenario['model']}_{scenario['pathway']}_{scenario['year']}"

            if db_name in databases:
                print(f"Skipping existing {db_name}...")
            else:
                new_scenarios.append(scenario)

        print(f"Creating {len(new_scenarios)} new future databases...", end="\n\t")
        print(*new_scenarios, sep="\n\t", end="\n")
        return new_scenarios


# Main function
def FutureScenarios(scenario_list):
    """
    Create future databases with premise.

    This function processes scenarios and creates new databases based on the premise module. It configures and uses user-defined settings and parameters for database creation and scenario processing.

    :returns: None
        The function does not return any value but performs operations to create and configure databases in Brightway2 based on specified scenarios.

    :raises Exception: If an error occurs during the processing of scenarios or database creation.
    """
    print("*** Starting FutureScenarios.py ***")
    print(f"\tUsing premise version {pm.__version__}")

    # Delete existing project if specified
    bd.projects.purge_deleted_directories()
    if project_premise in bd.projects and delete_existing_premise_project:
        bd.projects.delete_project(project_premise, True)
        print(f"Deleted existing project {project_premise}")

        bd.projects.set_current(project_premise_base)
        bd.projects.copy_project(project_premise)
        print(f"Created new project {project_premise} from {project_premise_base}")

    # Use existing project if available and deletion not required
    elif project_premise in bd.projects and not delete_existing_premise_project:
        print(f"Project {project_premise} already exists, we will use it")
        bd.projects.set_current(project_premise)

    # Create new project
    else:
        bd.projects.set_current(project_premise_base)
        bd.projects.copy_project(project_premise)
        print(f"Created new project {project_premise} from {project_premise_base}")
        print(f"Using database {database_name}")
        print("Removing unneeded databases..")
        for db in list(bd.databases):
            if db != database_name and "biosphere" not in db:
                del bd.databases[db]
                print(f"Removed {db}")

    # Clear cache if deletion is required (may not be necessary, but can help overcome errors sometimes)
    # if delete_existing_premise_project:
    #     pm.clear_cache()

    count = 0
    db_parts = database_name.split("-")
    version = db_parts[-2]
    model = db_parts[-1]

    print(f"\n** Using: {database_name}**")
    print()

    # Loop through scenario batches
    for scenarios_set in grouper(scenario_list, batch_size):
        if len(scenario_list) < batch_size:
            total_batches = 1
            scenarios_set = scenario_list

        else:
            total_batches = math.ceil(len(scenario_list) / batch_size)

        count += 1
        print(
            f"\n ** Processing scenario set {count} of {total_batches}, batch size {batch_size} **"
        )
        logging.info(
            f"\n ** Processing scenario set {count} of {total_batches}, batch size {batch_size} **"
        )

        model_args = {
            "range time": 2,
            "duration": False,
            "foresight": False,  # vs. myopic. shoul match the scenario, IMAGE = False, REMIND = True
            "lead time": True,  # otherwise market average is used
            "capital replacement rate": True,  # otherwise, baseline is used
            "measurement": 0,  # [slope, linear, area, weighted-slope, split]
            "weighted slope start": 0.75,  # only for method 3
            "weighted slope end": 1.00,  # only for method 3
        }

        # Create new database based on scenario details
        ndb = pm.NewDatabase(
            scenarios=scenarios_set,
            source_db=database_name,
            source_version=version,
            system_model=model,
            key=premise_key,
            use_multiprocessing=use_mp,
            system_args=model_args,
            quiet=premise_quiet,
            keep_uncertainty_data=True,
        )

        try:
            ndb.update_all()
            ndb.update_cars()
            ndb.update_buses()
            # ndb.update_trucks()
            # ndb.update_two_wheelers()
            # ndb.update_electricity()
            # ndb.update_cement()
            # ndb.update_steel()
            # ndb.update_fuels()
            # ndb.update_emissions()
            # ndb.update_dac()
        except Exception as e:
            print(f"Error: {e}")

        # Write the new database to brightway
        ndb.write_db_to_brightway()

    # Add GWP factors to the project
    add_premise_gwp()
    print("***** Done! *****")
    logging.info("Done!")

    # change back to the original directory
    os.chdir(Path(__file__).parent)


def MakeFutureScenarios():
    """
    Main function to run the FutureScenarios module.
    Only activated if `use_premise` is set to True in `user_settings.py`.

    Calls the `FutureScenarios` function to create new databases based on the list of scenarios and settings specified in `user_settings.py`.
    """

    if use_premise:
        available_scenarios = make_possible_scenario_list(
            filenames, desired_scenarios, years
        )
        scenario_list = check_existing(available_scenarios)
        FutureScenarios(scenario_list)
    else:
        print("Premise not called for, continuing...")


# Run the main function
if __name__ == "__main__":
    MakeFutureScenarios()
