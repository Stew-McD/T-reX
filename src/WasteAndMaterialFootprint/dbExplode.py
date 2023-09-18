#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dbExplode returns a single level list of all exchanges in a given Brightway2 database

It uses wurst to open up the database, explode to a list of all exchanges, and save in a DataFrame as a .pickle binary file.

This function will copy 'default' to a new project called 'WasteAndMaterialFootprint'. If 'WasteAndMaterialFootprint'  exists, it will be deleted and re-made each time.

GIVE PROJECT AND DB NAMES AS STRINGS OR LEAVE BLANK TO USE DEFAULTS

Examples of project and db names:
project_base='default_cutoff38'
project_wasteandmaterial='WasteAndMaterialFootprint_cutoff38'
db="cutoff38"
db_wasteandmaterial="db_wasteandmaterial_cutoff38"

Created on Wed Nov 16 11:31:38 2022
@author: SC-McD
based on the work of LL
"""
from datetime import datetime
import pandas as pd
import os

import bw2data as bd
import wurst as w

def dbExplode(project_base, project_wasteandmaterial, db_name):



    print("** dbExplode uses wurst to open a bw2 data base, \nexplodes the exchanges for each process, \nthen returns a pickle file with a DataFrame list of all activities **")
    print("\n * Using packages: ",
          "\n\t bw2data", bd.__version__,
          "\n\t wurst", w.__version__)

    if project_wasteandmaterial in bd.projects:
        print("WasteAndMaterial project already exists:" + project_wasteandmaterial)
        bd.projects.delete_project(project_wasteandmaterial, delete_dir=True)
        print("WasteAndMaterial project deleted:" + project_wasteandmaterial)

    if project_wasteandmaterial not in bd.projects:
        print("\n**Project {} will be copied to a new project: {}".format(project_base, project_wasteandmaterial))
        bd.projects.set_current(project_base)
        bd.projects.copy_project(project_wasteandmaterial)

    # else:
    #     print("\n** We will use project: {}".format(project_wasteandmaterial))
    #     bd.projects.set_current(project_wasteandmaterial)

# Explode database
    db = bd.Database(db_name)
    print("\n* db:", db.name, "in project:",
          bd.projects.current, "will be processed")
    print("\n** Opening the sausage... \n")
    guts = w.extract_brightway2_databases(db.name)

    print("\n*** Extracting activities from db...")
    df = pd.DataFrame(guts, columns=[
                      'code', 'name', 'location', 'reference product', 'categories', 'classifications', 'exchanges'])

    print("\n*** Exploding exchanges from activities...")
    df = df.explode("exchanges", ignore_index=True)
    df_ex = pd.json_normalize(df.exchanges, max_level=0)
    df_ex = df_ex[['name', 'amount', 'unit', 'product',
                   'production volume', 'type', 'location']]
    df_ex = df_ex.add_prefix("ex_")

    df = df.join(df_ex)
    df = df.drop("exchanges", axis=1)
    df.set_index('code', inplace=True)

# saves the list of exchanges as a pickle
    print("\n*** Pickling...")
    tmp = os.getcwd() + "/data/tmp/"
    if not os.path.isdir(tmp):
        os.makedirs(tmp)
    pickle_path = os.path.join(tmp, db.name + "_exploded.pickle")
    df.to_pickle(pickle_path)
    print("\n Pickle is:", "%1.0f" %
          (os.path.getsize(pickle_path)/1024**2), "MB")
    print("\n*** The sausage <"+db.name +
          "> was exploded and pickled.\n\n Rejoice!\n")

# make log file
    log_entry = (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "," + db.name + "," + bd.projects.current)
    log_file = os.path.join(tmp, 'dbExplode.log')
    with open(log_file, 'a') as l:
        l.write(str(log_entry)+"\n")

    return
