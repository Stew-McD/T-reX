#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sat Feb 11 10:02:15 2023
@author: Stew-McD
"""

import os
import bw2data as bd
import pandas as pd
from default_materials import default_materials
from user_settings import dir_tmp, dir_config, dir_logs, dir_searchmaterial_results


def SearchMaterial(db_name, project_wasteandmaterial):
    """
    Search for materials in a specified database and extract related information.

    This function takes a database name as input, sets the project to the respective database,
    and looks for activities involving a predefined list of materials. The function extracts
    relevant details of these activities, such as ISIC and CPC classifications, and saves
    the details to a CSV file. It also extracts related material exchanges and saves them
    to another CSV file.

    Parameters:
    db_name (str): The name of the database to search in.

    Returns:
    None

    Raises:
    Exception: If there is any error in reading the materials list from the file.
    """

    # Configuring search result directories
    dir_searchmaterial_results_db = dir_searchmaterial_results / db_name
    dir_searchmaterial_results_grouped = dir_searchmaterial_results_db / "grouped"

    # Ensure necessary directories exist
    for directory in [dir_tmp, dir_logs, dir_searchmaterial_results_grouped]:
        if not directory.exists():
            directory.mkdir(parents=True)
    print("\n*** Starting SearchMaterial ***")
    print("*** Loading pickle to dataframe...")
    pickle_path = dir_tmp / f"{db_name}_exploded.pickle"
    df = pd.read_pickle(pickle_path)

    # Set the current project
    bd.projects.set_current(project_wasteandmaterial)

    # Load the database
    db = bd.Database(db_name)
    print(
        f"\n*** Loading activities \nfrom database: {db.name} \nin project: {project_wasteandmaterial}"
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
        materials = default_materials

    # Display loaded materials
    print(f"\n** Materials ({len(materials)}):\n")
    print(*materials, sep="\n")

    # Filter activities based on the materials list
    materials_df = pd.DataFrame(default_materials, columns=["name", "group"])
    materials_dict = dict(materials)
    acts = acts_all[acts_all["name"].isin(materials_df.name)].reset_index(drop=True)
    acts["material_group"] = acts["name"].map(materials_dict)

    print(f"\nThe following {len(acts)} material markets were found:")
    print(acts[["name", "material_group", "location"]].sort_values(by="name"))

    # Extract and populate ISIC and CPC classifications using a function and apply
    def extract_classifications(row):
        for classification in row["classifications"]:
            if "ISIC" in classification[0]:
                row["ISIC"] = classification[1]
            if "CPC" in classification[0]:
                row["CPC"] = classification[1]
        return row

    acts = acts.apply(extract_classifications, axis=1)
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
    hits["material_group"] = hits["ex_name"].map(materials_dict)

    # Save exchanges to CSV
    file_name = dir_searchmaterial_results_db / "material_exchanges.csv"
    hits.to_csv(file_name, sep=";")
    print(f"\nThere were {len(hits)} matching exchanges found in {db_name}")
    print(f"\nSaved material exchanges to csv:\n{file_name}")

    # Generate and save grouped exchanges
    print("\n*** Grouping material exchanges by material group ***")
    for group in sorted(hits.material_group.unique()):
        df_group = hits[hits.material_group == group]
        file_name = dir_searchmaterial_results_grouped / f"MaterialDemand_{group}.csv"
        df_group.to_csv(file_name, sep=";")
        print(f"\t{group} : {len(df_group)}")

    return None
