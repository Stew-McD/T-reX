"""
SearchWaste Module
==================

This script loads data from '<db name>_exploded.pickle', runs search queries, 
and produces CSV files to store the results and a log entry. The search queries are 
formatted as dictionaries with fields NAME, CODE, and search terms keywords_AND, 
keywords_OR, and keywords_NOT. These queries are defined in `config/queries_waste.py`.

Functionality
-------------
Provides a function, :func:`SearchWaste`, that loads data from '<db name>_exploded.pickle',
runs search queries, and produces result CSVs and log entries.
"""

import os
import shutil
from datetime import datetime

import pandas as pd
from config.queries_waste import queries_waste
from config.user_settings import dir_logs, dir_searchwaste_results, dir_tmp


def SearchWaste(db_name, dir_searchwaste_results=dir_searchwaste_results):
    """
    Load data from '<db name>_exploded.pickle', run search queries, and produce
    result CSVs and log entries.

    This function processes waste-related data from a given database and runs
    predefined queries to identify relevant waste exchanges. The results are
    saved in CSV files and log entries are created for each search operation.

    :param str db_name: The database name to be used in the search operation.

    Note:
    The queries are defined in `config/queries_waste.py`.
    """



    print("\n*** Starting SearchWaste ***")

    dir_searchwaste_results = os.path.join(dir_searchwaste_results, db_name)
    if os.path.isdir(dir_searchwaste_results):
        print("Deleting existing results directory")
        shutil.rmtree(dir_searchwaste_results)

    # Ensure necessary directories exist
    if not os.path.exists(dir_logs):
        os.makedirs(dir_logs)
    if not os.path.exists(dir_searchwaste_results):
        os.makedirs(dir_searchwaste_results)

    # Load dataset
    pickle_path = os.path.join(dir_tmp, db_name + "_exploded.pickle")
    if os.path.isfile(pickle_path):
        df = pd.read_pickle(pickle_path)
        print("*** Loading pickle to dataframe ***")
    else:
        print("Pickle file does not exist.")
        return

    print("*** Searching for waste exchanges ***")

    def search(query):
        """
        Execute an individual search query on the dataset.

        Parameters:
        - query (dict): Search query defined in `config/queries_waste.py`.

        Returns:
        A CSV file with search results, saved to `data/SearchWasteResults/<db_name>` with the query name.
        """

        # Extract and process query components (for readability in the code)
        NAME_BASE = query["name"]
        UNIT = query["unit"]
        NAME = NAME_BASE + "-" + UNIT
        CODE = NAME.replace(" ", "")
        query.update({"code": NAME, "db_name": db_name})
        AND = query["AND"]
        OR = query["OR"]
        NOT = query["NOT"]
        DBNAME = query["db_name"]

        # Apply the search terms to the dataframe
        df_results = df[
            (df["ex_name"].apply(lambda x: all(i in x for i in AND)))
            & (df["ex_unit"] == UNIT)
            & (df["ex_amount"] != 0)
            # & (df["ex_amount"] != -1)
        ].copy()

        # Apply OR and NOT search filters
        if OR:
            df_results = df_results[
                df_results["ex_name"].apply(lambda x: any(i in x for i in OR))
            ]
        if NOT:
            df_results = df_results[
                df_results["ex_name"].apply(lambda x: not any(i in x for i in NOT))
            ]

        # Save results to CSV
        wasteandmaterial_file_name = NAME.replace(" ", "")
        wasteandmaterial_file = os.path.join(
            dir_searchwaste_results, wasteandmaterial_file_name
        )
        df_results["database"] = DBNAME
        if df_results.shape[0] != 0:
            df_results.to_csv(wasteandmaterial_file + ".csv", sep=";")

        # Log the results
        log_entry = (
            f"TIME: {datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}, DB: {db_name}, RESULTS: {df_results.shape[0]}, "
            f"NAME: {query['name']}, Search parameters, AND={query['AND']}, OR={query['OR']}, NOT={query['NOT']}, "
            f"UNIT={query['unit']}, CODE={CODE}"
        )

        date = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(dir_logs, f"SearchWaste_{date}.log")
        with open(log_file, "a") as l:
            l.write(str(log_entry) + "\n")

        print(
            f"\t{query['name']:<25} \t| {query['unit']:<13} \t| {df_results.shape[0]:>6}"
        )

    # Execute each query using the search() function defined above
    for query in queries_waste:
        search(query)

    print("*** Finished searching for waste exchanges ***")

    return None
