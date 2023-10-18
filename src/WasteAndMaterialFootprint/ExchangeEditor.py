'''
|===============================================================|
| File: ExchangeEditor.py                                       |
| Project: WasteAndMaterialFootprint                            |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint |
| Description: <<description>>                                  |
|---------------------------------------------------------------|
| File Created: Monday, 18th September 2023 11:21:13 am         |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                              |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Wednesday, 18th October 2023 9:40:06 am        |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|

ExchangeEditor():
For every activity identified by WasteAndMaterialSearch(), this function appends the pertinent exchange 
from the db_wmf. This is the most time-consuming function, taking around 10 minutes per database.

Created on Thu Nov 17 15:30:24 2022
@author: Stew-McD
based on the work of LL
'''


def ExchangeEditor(project_wmf, db_name, db_wmf_name):
    """
    Modify the specified project's database to append relevant exchanges
    from the db_wmf for every activity identified by WasteAndMaterialSearch().

    For each exchange found, this function identifies the process, and then adds
    a new exchange to that process in the `db_wmf`. The new exchange
    replicates the same amount and unit as the original technosphere waste and material exchange.

    Parameters:
    - project_wmf (str): Name of the Brightway2 project to be modified.
    - db_name (str): Name of the database within the project where activities and exchanges are stored.
    - db_wmf_name (str): Name of the database containing waste and material exchange details.

    Returns:
    None

    Side Effects:
    - Modifies the given Brightway2 project by appending exchanges.
    - Writes log entries with statistics on added exchanges to a log file.

    Notes:
    The function reads files produced by both SearchWaste() and SearchMaterial()
    to determine which exchanges need to be added.

    This function is computationally intensive and might take approximately 30-60 minutes per database, depending on the number of exchanges to edit.
    """

    # Import necessary libraries
    from tqdm import tqdm
    import os
    import pandas as pd
    import bw2data as bd
    from datetime import datetime

    # Import user settings and directory paths
    from user_settings import (
        dir_logs,
        dir_searchwaste_results,
        dir_searchmaterial_results,
    )

    # Set the current project to project_wmf
    bd.projects.set_current(project_wmf)

    # Get database objects
    db = bd.Database(db_name)
    db_wmf = bd.Database(db_wmf_name)

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

    # Create a DataFrame for each file and store in the dictionary
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
            ]
        ]
        file_dict[key] = df

    # Start adding exchanges
    print("\n\n*** ExchangeEditor() is running for " + db_name + " ***\n")
    print(
        f"* Appending waste and material exchanges in:*\n*\t{db_wmf_name}\n *"
    )
    countNAME = 0

    # Iterate over each category (NAME)
    for NAME, df in file_dict.items():
        countNAME += 1
        start = datetime.now()
        progress_db = str(countNAME) + "/" + str(len(file_dict.items()))
        count = 0

        # For each exchange in the current category's DataFrame
        for exc in tqdm(df.to_dict("records"), desc=f" * {progress_db} - {NAME}: "):
            # Extract details of the exchange
            code, name, location, ex_name, amount, unit, ex_location = (
                exc["code"],
                exc["name"],
                exc["location"],
                exc["ex_name"],
                exc["ex_amount"],
                exc["ex_unit"],
                exc["ex_location"],
            )

            # Retrieve the process and wasteandmaterial exchange from the databases
            try:
                process = db.get(code)
            
                wasteandmaterial_ex = db_wmf.get(NAME)

                before = len(process.exchanges())

                # Create a new exchange in the process
                process.new_exchange(
                    input=wasteandmaterial_ex.key,
                    amount=amount,
                    unit=unit,
                    type="biosphere",
                ).save()
                after = len(process.exchanges())


                # If the exchange was successfully added, increment the counter
                if (after - before) == 1:
                    count += 1

            except:
                print(f"Process {name}, {ex_location} not found in {db_name}")
                continue
            
        # Log the time taken and number of additions for this category
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
            dir_logs, f'{datetime.now().strftime("%m%d%Y")}_ExchangeEditor.txt'
        )
        with open(log_file, "a") as l:
            l.write(str(log_entry) + "\n")

    print(f"\n*** ExchangeEditor() completed for {db_name} in {str(duration)} ***\n")

    # del bd.databases[db_wmf_name]
    return None
