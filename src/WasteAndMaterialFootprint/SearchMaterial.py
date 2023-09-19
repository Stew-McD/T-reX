#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 10:02:15 2023

@author: stew
"""
#%%

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

    # Importing the default materials list
    from default_materials import default_materials
    from user_settings import dir_tmp

    if not os.path.isdir(dir_tmp): os.makedirs(dir_tmp)

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
        with open('list_materials.txt') as f:
            materials = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as exc:
        print(f'Something went wrong, using the default material list... \nError: {exc}')
        materials = default_materials

    # Filtering activities based on the materials list and location
    acts = acts_all[(acts_all['name'].isin(materials)) & (acts_all['location'].isin(['GLO', 'RoW']))]
    acts = acts.reset_index(drop=True)

    # Printing the number of material markets found
    print("\nmaterial markets:", len(acts.name))
    print(acts.name)

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
    f = "data/activities_list_materials_"+db_name+".csv"
    print("\nSaved activities list to csv:", f)
    acts.to_csv(f, sep=";", index=False)

    # Loading a pickle file into a DataFrame
    pickle_path = os.path.join(dir_tmp, db_name+"_exploded.pickle")
    print("*** Loading pickle to dataframe...")
    df = pd.read_pickle(pickle_path)

    # Removing the classifications column from the DataFrame
    df.pop("classifications")
    print("*** Searching for material exchanges...")

    # Finding and saving material exchanges to a CSV file
    hits = df[df['reference product'].isin(acts["reference product"].values)]
    hits["database"] = db_name
    hits.to_csv(dir_tmp +'/material_exchanges_'+db_name+".csv", sep=";")
    
    # The function returns None
    return


