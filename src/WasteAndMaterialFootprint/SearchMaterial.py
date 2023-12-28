"""
SearchMaterial Module
=====================

This script loads data from '<db name>_exploded.pickle', runs search queries, 
and produces a CSV to store the results and a log entry. The search queries are 
formatted as dictionaries with fields NAME, CODE, and search terms keywords_AND, 
keywords_OR, and keywords_NOT. These queries are defined in `config/queries_waste.py`.

"""

import os
import shutil

import bw2data as bd
import pandas as pd
from config.queries_materials import queries_materials
from config.user_settings import (
    dir_config,
    dir_logs,
    dir_searchmaterial_results,
    dir_tmp,
)


def SearchMaterial(db_name, project_wmf):
    """
    Search for materials in a specified database and extract related information.

    This function takes a database name as input, sets the project to the respective database,
    and looks for activities involving a predefined list of materials. It extracts relevant details
    of these activities, such as ISIC and CPC classifications, and saves the details to a CSV file.
    It also extracts related material exchanges and saves them to another CSV file.

    :param db_name: The name of the database to search in.
    :param project_wmf: The Brightway2 project to set as current for the search.
    :return: None
    :raises Exception: If there is any error in reading the materials list from the file.
    """

    # Configuring search result directories
    dir_searchmaterial_results_db = dir_searchmaterial_results / db_name
    dir_searchmaterial_results_grouped = dir_searchmaterial_results_db / "grouped"

    if os.path.isdir(dir_searchmaterial_results_db):
        print("Deleting existing results directory")
        shutil.rmtree(dir_searchmaterial_results_db)

    # Ensure necessary directories exist
    for directory in [dir_tmp, dir_logs, dir_searchmaterial_results_grouped]:
        if not directory.exists():
            directory.mkdir(parents=True)
    print("\n*** Starting SearchMaterial ***")
    pickle_path = dir_tmp / f"{db_name}_exploded.pickle"

    if os.path.isfile(pickle_path):
        df = pd.read_pickle(pickle_path)
        print("*** Loading pickle to dataframe ***")
    else:
        print("Pickle file does not exist.")
        return

    # Set the current project
    bd.projects.set_current(project_wmf)

    # Load the database
    db = bd.Database(db_name)
    print(
        f"\n*** Loading activities \nfrom database: {db.name} \nin project: {project_wmf}"
    )

    # Extracting activities from the database
    acts_all = pd.DataFrame([x.as_dict() for x in db])
    acts_all = acts_all[
        [
            "code",
            "name",
            "unit",
            "location",
            "reference product",
            "classifications",
            "database",
            "production amount",
        ]
    ]

    # Load the materials list
    try:
        with open(dir_config / "list_materials.txt") as f:
            materials = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
            print(
                f"\nLoaded materials list from file: {dir_config / 'list_materials.txt'}"
            )
    except Exception:
        print("Using the default material list")
        materials = queries_materials

    # Display loaded materials
    print(f"\n** Materials ({len(materials)}) | (activity, group)\n", end="\t")
    print(*materials, sep="\n\t")



    def map_materials(name):
        for key, value in materials_dict.items():
            if name.startswith(key):
                return value
        return "***"  # or return a default value

    acts["material_group"] = acts["name"].apply(map_materials)

    print(f"\n* {len(acts)} material markets were found:")
    print(acts[["name", "material_group", "location"]].sort_values(by="name"))

    # Extract and populate ISIC and CPC classifications
    def extract_classifications(row, acts):
        """
        Extracts classifications (CPC, ISIC, etc.) from the list of classifications and adds them as columns to the dataframe

        :param pd.Series row: A row of the dataframe
        :param pd.DataFrame acts: The DataFrame containing activities data

        :returns pd.Series row: The row with the classifications added as columns
        """

        # Check if the "classifications" column exists and is in the correct format
        if not isinstance(row["classifications"], list):
            print(
                f'\tError for activity: {row["name"]}, classification: {row["classifications"]}'
            )
            print(
                f'\t\tInferring from reference product base: "{row["reference product"].split(",")[0]}", from reference product "{row["reference product"]}"'
            )

            # Find activities with the same or similar "reference product"
            matching_activities = acts[
                acts["reference product"] == row["reference product"].split(",")[0]
            ]

            if not matching_activities.empty:
                # Choose the first matching activity and use its classifications
                inferred_classifications = matching_activities.iloc[0][
                    "classifications"
                ]
                row["classifications"] = inferred_classifications
            else:
                print(
                    f'No matching activities found for reference product: {row["reference product"]}'
                )

        # If the "classifications" column is a list, extract the values
        if isinstance(row["classifications"], list):
            for classification in row["classifications"]:
                # Split the classification into code and value
                code, value = classification
                # Add a new column with the classification code and set its value
                row[code] = value

        return row

    print("\n* Extracting classifications...\n")
    acts = acts.apply(lambda row: extract_classifications(row, acts), axis=1)
    acts.drop("classifications", axis=1, inplace=True)

    # Save activities to a CSV
    acts.to_csv(
        dir_searchmaterial_results_db / "material_activities.csv", sep=";", index=False
    )
    print(
        f"\nSaved activities list to csv: \n{dir_searchmaterial_results_db / 'material_activities.csv'}"
    )

    # Load and filter exchanges
    print(f"\n*** Searching for material exchanges in {db_name} ***")
    print("\n*** Loading pickle to dataframe ***")
    df = pd.read_pickle(pickle_path)
    df = df[df.ex_type == "technosphere"]
    df.pop("classifications")

    hits = df[df["ex_name"].isin(acts["name"].values)].copy()
    hits["database"] = db_name
    hits["material_group"] = hits["ex_name"].apply(map_materials)

    # Save exchanges to CSV
    file_name = dir_searchmaterial_results_db / "material_exchanges.csv"
    hits.to_csv(file_name, sep=";")
    print(f"\nThere were {len(hits)} matching exchanges found in {db_name}")
    print(f"\nSaved material exchanges to csv:\n{file_name}")

    # Generate and save grouped exchanges
    print("\n*** Grouping material exchanges by material group \n")
    for group in sorted(hits.material_group.unique()):
        df_group = hits[hits.material_group == group]
        file_name = (
            dir_searchmaterial_results_grouped / f"MaterialFootprint_{group}.csv"
        )
        df_group.to_csv(file_name, sep=";")
        print(f"\t{len(df_group):>6} : {group}")

    return None
