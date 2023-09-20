#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 10:02:15 2023

@author: stew
"""

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
    import os
    import bw2data as bd
    import pandas as pd

    # Add the config dir to the Python path
    # import sys
    # from pathlib import Path
    # cwd = Path.cwd()
    # dir_config = cwd.parents[1] / 'config'
    # sys.path.insert(0, str(dir_config))

    # Importing the default materials list
    from default_materials import default_materials
    from user_settings import dir_tmp, dir_config, dir_logs, dir_searchmaterial_results

    dir_searchmaterial_results = dir_searchmaterial_results / db_name
    dir_searchmaterial_results_grouped = dir_searchmaterial_results / 'grouped'

    if not os.path.isdir(dir_tmp): os.makedirs(dir_tmp)
    if not os.path.isdir(dir_logs): os.makedirs(dir_logs)
    if not os.path.isdir(dir_searchmaterial_results_grouped): os.makedirs(dir_searchmaterial_results_grouped)

    # load exchanges into df from the dbExplode pickle file
    pickle_path = os.path.join(dir_tmp, db_name+ "_exploded.pickle")
    print("*** Loading pickle to dataframe...")
    df = pd.read_pickle(pickle_path)

    # Setting the current project to the default project associated with the database name
    bd.projects.set_current(project_wasteandmaterial)

    # Loading the database
    db = bd.Database(db_name)

    # Printing the loading status
    print("\nLoading activities from database:", db.name, 'in project:', project_wasteandmaterial)

    # Creating a DataFrame of all activities with specific details
    acts_all = pd.DataFrame([x.as_dict() for x  in db])
    acts_all = acts_all[['code','name','unit','location','activity type','reference product', 'classifications', 'database', 'production amount',]]

    # Loading the list of materials to search for
    try:
        with open(dir_config / 'list_materials.txt') as f:
            materials = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print("\nLoaded materials list from file:", dir_config / 'list_materials.txt')
    except Exception as exc:
        print('Using the default material list')
        materials = default_materials

    # Printing the number of materials found
    print("\n** Materials:", len(materials), "\n")
    print(*materials, sep="\n")

    # Creating a DataFrame of the materials list
    materials_df = pd.DataFrame(default_materials, columns=['name', 'group'])
    
    # Creating a dictionary of the materials list
    materials_dict = dict(materials)
    materials_dict_nomarket = {k.replace("market for ", ""): v for k, v in materials_dict.items()}

    # Filtering activities based on the materials list
    acts = acts_all[(acts_all['name'].isin(materials_df.name))]
    acts = acts.reset_index(drop=True)
    acts['material_group'] = acts['name'].map(materials_dict)

    # Printing the number of material markets found
    print(f"\nThe following {len(acts)} material markets were found")
    acts_info = acts[['name', 'material_group', 'location']]
    print(acts_info.sort_values(by='name'))

    # Extracting ISIC and CPC classifications
    print("\nExtracting classification data")
    acts.loc[:,"ISIC"] = ''
    acts.loc[:,"CPC"] = ''
    for i, j in acts.iterrows():
        for k in j["classifications"]:
            if "ISIC" in k[0]:
                acts.loc[i,'ISIC'] = k[1]
            if "CPC" in k[0]:
                acts.loc[i,'CPC'] = k[1]

    # Removing the classifications column
    acts = acts.drop("classifications", axis=1)

    # Saving the activities list to a CSV file
    f = dir_searchmaterial_results / "material_activities.csv"
    print("\nSaved activities list to csv:", f)
    acts.to_csv(f, sep=";", index=False)

    # Loading the pickle file of the exploded database into a DataFrame
    pickle_path = os.path.join(dir_tmp, db_name+"_exploded.pickle")
    print("\n ** Loading pickle to dataframe...")
    df = pd.read_pickle(pickle_path)
    df = df[df.ex_type == "technosphere"]

    # Removing the classifications column from the DataFrame
    df.pop("classifications")
    print("*** Searching for material exchanges...")

    # Finding and saving material exchanges to a CSV file
    hits = df[df['ex_name'].isin(acts["name"].values)].copy()

    # Adding the database name and material group to the DataFrame
    hits.loc[:, "database"] = db_name
    hits.loc[:, "material_group"] = hits["ex_name"].map(materials_dict)
    file_name = dir_searchmaterial_results / "material_exchanges.csv"
    hits.to_csv(file_name, sep=";")

    # Printing the number of material exchanges found
    print(f"\nThere were: {len(hits)} matching exchanges found in {db_name}")
    print("\nSaved material exchanges to csv:", file_name)

    # make a separate csv for each material group
    for group in hits.material_group.unique():
        print(f"\nThere were: {len(hits[hits.material_group == group])} matching exchanges found in {db_name} for {group}")
        df = hits[hits.material_group == group]
        file_name = dir_searchmaterial_results_grouped / f"MaterialDemand_{group}.csv"
        df.to_csv(file_name, sep=";")
        print("\tSaved to csv:", file_name)

    return
