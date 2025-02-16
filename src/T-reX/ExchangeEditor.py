"""
ExchangeEditor Module
=====================

This module is responsible for editing exchanges with wurst and Brightway2.
It appends relevant exchanges from the `db_T_reX` (database containing waste and material exchange details)
to activities identified by `WasteAndMaterialSearch()` in the specified project's database (`db_name`).
Each appended exchange replicates the same amount and unit as the original technosphere waste and material exchange.

"""

# Imports
import os
from datetime import datetime
import bw2data as bd
import pandas as pd
from tqdm import tqdm


def ExchangeEditor(project_T_reX, db_name, db_T_reX_name):
    """
    Append relevant exchanges from `db_T_reX` to each activity in `db_name` identified by `WasteAndMaterialSearch()`.

    This function modifies the specified project's database by appending exchanges from the `db_T_reX` to activities identified by `WasteAndMaterialSearch()`. The appended exchanges mirror the quantity and unit of the original technosphere waste and material exchange.

    :param str project_T_reX: Name of the Brightway2 project to be modified.
    :param str db_name: Name of the database within the project where activities and exchanges are stored.
    :param str db_T_reX_name: Name of the database containing waste and material exchange details.

    :returns: None. Modifies the given Brightway2 project by appending exchanges and logs statistics about the added exchanges.
    :rtype: None

    :raises Exception: If any specified process or exchange is not found in the database.
    """

    # Import user settings and directory paths
    from config.user_settings import (
        dir_logs,
        dir_searchmaterial_results,
        dir_searchwaste_results,
    )

    # Set the current project to project_T_reX
    bd.projects.set_current(project_T_reX)

    # Get database objects
    db = bd.Database(db_name)
    db_T_reX = bd.Database(db_T_reX_name)

    # Define directories
    dir_searchwaste_results = dir_searchwaste_results / db_name
    dir_searchmaterial_results_grouped = (
        dir_searchmaterial_results / db_name / "grouped"
    )

    # Create a dictionary of files produced by SearchWaste() and SearchMaterial()
    file_dict = {
        os.path.splitext(f)[0]: os.path.join(dir_searchwaste_results, f)
        for f in os.listdir(dir_searchwaste_results)
    }
    file_dict.update(
        {
            os.path.splitext(f)[0]: os.path.join(dir_searchmaterial_results_grouped, f)
            for f in os.listdir(dir_searchmaterial_results_grouped)
        }
    )

    sorted_items = sorted(file_dict.items())
    file_dict = dict(sorted_items)

    # Create a DataFrame for each file and store it in the dictionary
    for key, f_path in file_dict.items():
        df = pd.read_csv(f_path, sep=";", header=0, index_col=0)
        df.reset_index(inplace=True)
        df = df[
            [
                "code",
                "name",
                "location",
                "ex_name",
                "ex_amount",
                "ex_unit",
                "ex_location",
                "database",
            ]
        ]
        file_dict[key] = df

    # Start adding exchanges
    print("\n\n*** ExchangeEditor() is running for " + db_name + " ***\n")
    print(f"* Appending waste and material exchanges in {db_T_reX_name}\n ")
    countNAME = 0
    # Calculate the maximum length of NAME
    max_name_length = max(len(name) for name in file_dict.keys())

    # Calculate the maximum length of progress_db
    max_progress_length = (
        len(str(len(file_dict.items()))) * 2 + 1
    )  # times 2 for countNAME and len(file_dict.items()), plus 1 for the slash

    # Define the bar format with a fixed width for desc
    bar_format = f"{{desc:<{max_progress_length + max_name_length + 10}}} | {{bar:30}} | {{percentage:3.1f}}% | Progress: {{n:>5}} of {{total:<5}} | Elapsed: {{elapsed:<5}} | Remaining: {{remaining:<5}}"

    start = datetime.now()
    # Iterate over each category (NAME)
    for NAME, df in sorted(file_dict.items(), reverse=False):
        countNAME += 1
        progress_db = f"{countNAME:2}/{len(file_dict.items())}"
        count = 0

        # For each exchange in the current category's DataFrame
        for exc in tqdm(
            df.to_dict("records"),
            desc=f" - {progress_db} : {NAME} ",
            bar_format=bar_format,
            colour="magenta",
            smoothing=0.01,
        ):
            # Extract details of the exchange
            code, name, location, ex_name, amount, unit, ex_location, database = (
                exc["code"],
                exc["name"],
                exc["location"],
                exc["ex_name"],
                exc["ex_amount"],
                exc["ex_unit"],
                exc["ex_location"],
                db_name,
            )

            KEY = (database, code)
            T_reX_KEY = (
                db_T_reX_name,
                NAME.split("_")[1]
                .capitalize()
                .replace("_", " ")
                .replace("-", " ")
                .replace("kilogram", "(kg)")
                .replace("cubicmeter", "(m3)"),
            )
            # Retrieve the process and T_reX exchange from the databases
            try:
                process = bd.get_activity(KEY)
                T_reX_ex = bd.get_activity(T_reX_KEY)
                before = len(process.exchanges())

                #! TODO: Check if the exchange already exists in the process, and if so, skip it
                # Create a new exchange in the process
                process.new_exchange(
                    input=T_reX_ex,
                    amount=amount,
                    unit=unit,
                    type="biosphere",
                ).save()
                after = len(process.exchanges())

                # If the exchange was successfully added, increment the counter
                if (after - before) == 1:
                    count += 1

            except Exception as e:
                print(e)
                print(f"Process {name}, {ex_location} not found in {db_name}")
                continue

        # Log the time taken and the number of additions for this category
        end = datetime.now()
        duration = end - start

        log_entry = (
            end.strftime("%m/%d/%Y, %H:%M:%S"),
            db_name,
            NAME,
            "additions",
            count,
            "duration:",
            str(duration),
        )
        log_file = os.path.join(
            dir_logs, f'{datetime.now().strftime("%Y-%m-%d")}_ExchangeEditor.txt'
        )
        with open(log_file, "a") as l:
            l.write(str(log_entry) + "\n")
    print(f'{"*"*100}')
    print(
        f"\n*** ExchangeEditor() completed for {db_name} in {str(duration).split('.')[0]} (h:m:s) ***\n"
    )
    print(f'{"*"*100}')

    return None
