"""
ExplodeDatabase Module
======================

This module is responsible for exploding a Brightway2 database into a single-level list of all exchanges.
It utilizes the wurst package to unpack the database, explode it to a list of all exchanges, and save this data 
in a DataFrame as a .pickle binary file.

"""

# Imports
import os
from datetime import datetime

import bw2data as bd
import pandas as pd
import wurst as w


def ExplodeDatabase(db_name):
    """
    Explode a Brightway2 database into a single-level list of all exchanges using wurst.

    :param str db_name: Name of the Brightway2 database to be exploded.

    :returns: None
        The function saves the output to a file and logs the operation, but does not return any value.
    :rtype: None
    """
    from config.user_settings import dir_logs, dir_tmp

    if not os.path.isdir(dir_tmp):
        os.makedirs(dir_tmp)
    if not os.path.isdir(dir_logs):
        os.makedirs(dir_logs)

    print("\n*** Starting ExplodeDatabase ***")
    print(
        "ExplodeDatabase uses wurst to open a bw2 database, explodes the exchanges for each process, and then returns a pickle file with a DataFrame list of all activities"
    )

    # Set the path to save the pickle file
    pickle_path = dir_tmp / f"{db_name}_exploded.pickle"

    # Extract information from the specified database
    db = bd.Database(db_name)
    print(f"\n** db: {db.name}, in project: {bd.projects.current} will be processed")

    # Unpack the database using wurst
    print("\n** Opening the sausage...")
    guts = w.extract_brightway2_databases(db_name)

    # Create a DataFrame from the extracted data
    print("\n*** Extracting activities from db...")
    df = pd.DataFrame(
        guts,
        columns=[
            "code",
            "name",
            "location",
            "reference product",
            "categories",
            "classifications",
            "exchanges",
        ],
    )

    # Expand the exchanges column into a new DataFrame and join it with the original data
    print("\n*** Exploding exchanges from activities...")
    df = df.explode("exchanges", ignore_index=True)
    df_ex = pd.json_normalize(df.exchanges, max_level=0)
    df_ex = df_ex[
        ["name", "amount", "unit", "product", "production volume", "type", "location"]
    ]
    df_ex = df_ex.add_prefix("ex_")
    df = df.join(df_ex)

    # Finalize the DataFrame by setting the index and removing the now redundant exchanges column
    df = df.drop("exchanges", axis=1)
    df.set_index("code", inplace=True)

    # Save the DataFrame as a pickle file
    print("\n*** Pickling...")
    df.to_pickle(pickle_path)
    print("\n Pickle is:", "%1.0f" % (os.path.getsize(pickle_path) / 1024**2), "MB")

    # Log the operation with a timestamp, database name, and project name
    print("\n*** The sausage <" + db.name + "> was exploded and pickled. Rejoice!")

    log_entry = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + ","
        + db.name
        + ","
        + bd.projects.current
    )

    log_file = dir_logs / f'{datetime.now().strftime("%Y-%m-%d")}_ExplodeDatabase.log'
    with open(log_file, "a") as l:
        l.write(str(log_entry) + "\n")

    return None
