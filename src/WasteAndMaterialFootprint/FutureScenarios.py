"""
FutureScenarios Module
======================

This module is responsible for creating future databases with premise.

Author: Stewart Charles McDowall
Email: s.c.mcdowall@cml.leidenuniv.nl
GitHub: Stew-McD
Institution: CML, Leiden University
Licence: The Unlicense


"""

# Imports
import logging
import os
from datetime import datetime
from itertools import zip_longest
from pathlib import Path

import bw2data as bd

# Import user settings or set defaults
try:
    from user_settings import (
        batch_size,
        database_name,
        delete_existing,
        dir_data,
        dir_logs,
        premise_key,
        premise_quiet,
        project_premise,
        project_premise_base,
        scenarios_all,
        use_mp,
        verbose,
    )

    print("\nUsing user_settings.py file\n")
except ImportError:
    print("No user_settings.py file found, using defaults")
    premise_key = None
    project_premise_base = "default"
    project_premise = "premise_default"
    database_name = "ecoinvent_3.9.1_cutoff"
    delete_existing = True
    batch_size = 1
    scenarios_all = [{"model": "remind", "pathway": "SSP2-Base", "year": 2050}]
    dir_logs = Path.cwd()
    verbose = False
    use_mp = False

# easiest way to stop premise from making a mess
dir_premise = dir_data / "premise"
if not os.path.exists(dir_premise):
    os.makedirs(dir_premise)
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


# Main function
def FutureScenarios():
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
    if project_premise in bd.projects and delete_existing:
        bd.projects.delete_project(project_premise, True)
        print(f"Deleted existing project {project_premise}")

        bd.projects.set_current(project_premise_base)
        bd.projects.copy_project(project_premise)
        print(f"Created new project {project_premise} from {project_premise_base}")

    # Use existing project if available and deletion not required
    elif project_premise in bd.projects and not delete_existing:
        print(f"Project {project_premise} already exists, we will use it")
        bd.projects.set_current(project_premise)

    # Create new project
    else:
        bd.projects.set_current(project_premise_base)
        bd.projects.copy_project(project_premise)
        print(f"Created new project {project_premise} from {project_premise_base}")
        print("Removing unneeded databases..")
        for db in list(bd.databases):
            if db not in [database_name] and "biosphere" not in db:
                del bd.databases[db]
                print(f"Removed {db}")

    # Clear cache if deletion is required
    if delete_existing:
        pm.clear_cache()

    count = 0
    db_parts = database_name.split("_")
    version = db_parts[-2]
    model = db_parts[-1]

    print(f"\n** Using: {database_name}, {version}, {model} **")

    # Loop through scenario batches
    for scenarios_set in grouper(scenarios_all, batch_size):
        if len(scenarios_all) < batch_size:
            total_batches = 1
            scenarios_set = scenarios_all

        else:
            total_batches = len(scenarios_all) // batch_size

        count += 1
        print(
            f"\n ** Processing scenario set {count} of {total_batches: .0f}, batch size {batch_size} **"
        )
        logging.info(
            f"\n ** Processing scenario set {count} of {total_batches : .0f}, batch size {batch_size} **"
        )

        model_args = {
            "range time": 2,
            "duration": False,
            "foresight": False,
            "lead time": True,
            "capital replacement rate": False,
            "measurement": 0,
            "weighted slope start": 0.75,
            "weighted slope end": 1.00,
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
        )

        # Updates depending on the model
        if model == "cutoff":
            ndb.update_all()
            ndb.update_cars()
            ndb.update_buses()

        if model == "consequential":
            ndb.update_all()
            # ndb.update_two_wheelers()
            ndb.update_electricity()
            ndb.update_cars()
            ndb.update_trucks()
            ndb.update_buses()
            ndb.update_cement()
            ndb.update_steel()
            ndb.update_fuels()
            ndb.update_emissions()
            ndb.update_dac()

        # Write the new database to brightway
        ndb.write_db_to_brightway()

    # Add GWP factors to the project
    add_premise_gwp()
    print("***** Done! *****")
    logging.info("Done!")

    # change back to the original directory
    os.chdir(Path(__file__).parent)


# Run the main function
if __name__ == "__main__":
    FutureScenarios()
