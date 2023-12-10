"""
VerifyDatabase Module
=====================

This module contains a function to verify a (WasteAndMaterialFootprint) database 
within a given project in Brightway2. It performs a verification by calculating LCA scores 
for random activities within the specified database using selected methods.

Author: Stewart Charles McDowall
Email: s.c.mcdowall@cml.leidenuniv.nl
GitHub: Stew-McD
Institution: CML, Leiden University
Licence: The Unlicense
"""

from datetime import datetime
from pathlib import Path
from random import choice

import bw2calc as bc
import bw2data as bd


def VerifyDatabase(
    project_name, database_name, check_material=True, check_waste=True, log=True
):
    """
    Verifies a database within a given project in Brightway2 by calculating LCA scores
    for random activities using selected methods.

    This function assesses the integrity and validity of a specified database within a Brightway2 project.
    It performs LCA calculations on random activities using Waste Footprint and Material Demand Footprint methods,
    and logs the results.

    :param str project_name: The name of the Brightway2 project.
    :param str database_name: The name of the database to be verified.
    :param bool check_material: If True, checks for Material Demand Footprint methods.
    :param bool check_waste: If True, checks for Waste Footprint methods.
    :param bool log: If True, logs the results.
    :return: Exit code (0 for success, 1 for failure).
    """

    # setup to log the result
    exit_code = 0
    if log:
        current_date = datetime.now().strftime("%Y%m%d")
        log_dir = Path("../../data/logs")
        if not log_dir.exists():
            log_dir = Path.cwd()
        log_file = log_dir / f"{current_date}_{project_name}.log"

    # Set the current project in Brightway2
    if project_name in bd.projects:
        bd.projects.set_current(project_name)
    else:
        print(f"Project {project_name} not found...")
        print(*bd.projects.report(), sep="\n")
        exit_code = 1
        return exit_code

    # screen for biosphere and WasteAndMaterialFootprint databases
    
    if any(word in database_name for word in ["biosphere","WasteAndMaterialFootprint"]):
        print(f"Skipping {database_name}...")
        exit_code = 0
        return exit_code
    
    
    # Load the database
    if database_name in bd.databases:
        bd.Database(database_name)
    else:
        print(f"Database {database_name} not found...")
        print(*bd.databases, sep="\n")
        exit_code = 1
        return exit_code

    print(f"\n** Verifying database {database_name} in project {project_name} **\n")

    # Initialize the score
    lca_score = 0
    count = 0
    # Loop until a non-zero score is obtained
    while lca_score == 0 and count < 5:
        try:
            count += 1
            # Get a random activity from the database
            act = bd.Database(database_name).random()

            # Initialize the list of methods
            methods = []

            # Find methods related to Waste Footprint
            if check_waste:
                methods_waste = [x for x in bd.methods if "Waste" in x[1]]
                methods += methods_waste

            # Find methods related to Material Demand Footprint
            if check_material:
                methods_material = [
                    x for x in bd.methods if "Demand" in x[1]
                ]
                methods += methods_material

            if not check_waste and not check_material:
                method = bd.methods.random()
                methods.append(method)

            # Choose a random method
            method = choice(methods)

            # Perform LCA calculation
            lca = bc.LCA({act: 1}, method)
            lca.lci()
            lca.lcia()

            # Get the lca score
            lca_score = lca.score

            # Print the result
            log_statement = f"\tScore: {lca_score:2.2e} \n\tMethod: {method[2]} \n\tActivity: {act['name']} \n\tDatabase: {database_name}\n"

        except Exception as e:
            # Print any errors that occur
            log_statement = (
                f"@@@@@@@@  Error occurred with '{database_name}': {e}! @@@@@@@@"
            )

            exit_code = 1
            break

        print(log_statement)
        # Log the result
        if log:
            with open(log_file, "a") as f:
                f.write(log_statement + "\n")

    return exit_code


if __name__ == "__main__":
    project_name = "WMF-default" # change this to the name of your project to run it independently
    database_name = "ecoinvent-3.9.1-cutoff" # also this
    exit_code = VerifyDatabase(
        project_name, database_name, check_material=True, check_waste=True, log=True
    )

    if exit_code == 0:
        print("** Database verified successfully! **")
    else:
        print("** Error occurred during verification! **")
        print(f"\t Look in the logfile for details. exit_code = {exit_code}")
