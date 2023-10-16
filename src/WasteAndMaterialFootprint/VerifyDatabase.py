"""
|===============================================================|
| File: VerifyDatabase.py                                       |
| Project: WasteAndMaterialFootprint                            |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint |
| Description: <<description>>                                  |
|---------------------------------------------------------------|
| File Created: Friday, 6th October 2023 8:31:42 pm             |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                              |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Monday, 16th October 2023 4:11:10 pm           |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|
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
    Verifies a (WasteAndMaterialFootprint) database
    within a given project in Brightway2.

    Parameters:
    project_name (str): The name of the Brightway2 project.
    database_name (str): The name of the database to be verified.

    Returns:
    None: Prints the lca score for a random activity.
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

    # Load the database
    if database_name in bd.databases:
        bd.Database(database_name)
    else:
        print(f"Database {database_name} not found...")
        print(*bd.databases, sep="\n")
        exit_code = 1
        return exit_code

    print(f"\n** Verifying database {database_name} in project {project_name} **")

    # Initialize the score
    lca_score = 0
    # Loop until a non-zero score is obtained
    while lca_score == 0:
        try:
            # Get a random activity from the database
            act = bd.Database(database_name).random()

            # Initialize the list of methods
            methods = []

            # Find methods related to Waste Footprint
            if check_waste:
                methods_waste = [x for x in bd.methods if "Waste Footprint" in x[0]]
                methods += methods_waste

            # Find methods related to Material Demand Footprint
            if check_material:
                methods_material = [
                    x for x in bd.methods if "Material Demand Footprint" in x[0]
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
            log_statement = f"{lca_score:2e}|{method[2]}|{act['name']}|{database_name}"

        except Exception as e:
            # Print any errors that occur
            log_statement = f"Error occurred with '{database_name}': {e}"

            exit_code = 1
            break

        print(log_statement)
        # Log the result
        if log:
            with open(log_file, "a") as f:
                f.write(log_statement + "\n")

    return exit_code


if __name__ == "__main__":
    project_name = "WMF-default"
    database_name = "ecoinvent_3.9.1_cutoff"
    exit_code = VerifyDatabase(
        project_name, database_name, check_material=True, check_waste=True, log=True
    )

    if exit_code == 0:
        print("** Database verified successfully! **")
    else:
        print("** Error occurred during verification! **")
        print(f"\t Look in the logfile for details. exit_code = {exit_code}")
