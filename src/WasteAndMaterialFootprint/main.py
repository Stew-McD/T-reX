#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*** This is the main module of the WasteAndMaterialFootprint tool ***

* To use the defaults, just run the whole script (but this will only work if you have the same format of project and database names)
* The terms of the waste search query can be edited config/queries_waste.py
* The list of materials can be edited in config/list_materials.txt
* The names of the projects and databases can be edited in config/user_settings.py

DEFAULTS:

EI database is of form 'cutoff38' or 'con39'
* versions = ["35", "38", "39", "391]
* models = ["cutoff", 'con', 'apos']

The script will copy the project "default"+<db_name> to project "WasteAndMaterialFootprint_"+<db_name>
* 'project_base': "default_"+<dbase>,
* 'project_wasteandmaterial': "WasteAndMaterialFootprint_"+<dbase>,


Created on Sat Nov 19 11:24:06 2022
@author: SC-McD
Based on the work of LL

"""
# %%% Imports
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
import bw2data as bd

cwd = Path.cwd()
sys.path.insert(0, str(cwd))

# Add the config dir to the Python path
dir_config = cwd.parents[1] / 'config'
sys.path.insert(0, str(dir_config))

# custom modules
from ExchangeEditor import ExchangeEditor
from MethodEditor import AddMethods
from ExplodeDatabase import ExplodeDatabase
from SearchWaste import SearchWaste
from SearchMaterial import SearchMaterial
from MakeCustomDatabase import dbWriteExcel, dbExcel2BW

# import configuration
from user_settings import args_list, dir_data, dir_tmp, dir_logs, dir_searchwaste_results, dir_searchmaterial_results

from queries_waste import queries_waste

# %% 1. DEFINE MAIN FUNCTION

args = args_list[0]

def WasteAndMaterialFootprint(args):

    print("\n*** Starting WasteAndMaterialFootprint ***\n")
    start = datetime.now()

    # %%% 1.0 Define the project names and database names based on the arguments given
    
    project_base = args['project_base']
    project_wasteandmaterial = args['project_wasteandmaterial']
    db_name = args['db_name']
    db_wasteandmaterial_name = args['db_wasteandmaterial_name']

    if project_wasteandmaterial in bd.projects:
        print(f"WasteAndMaterial project already exists: {project_wasteandmaterial}")
        redo = input("Do you want to delete it and start over? (y/n):  ")
        
        if redo == "y":
            bd.projects.delete_project(project_wasteandmaterial, delete_dir=True)
            print(f"WasteAndMaterial project deleted: {project_wasteandmaterial}")
        else:
            print("WasteAndMaterial project will not be deleted.")
            # sys.exit()

    if project_wasteandmaterial not in bd.projects:
        print(f"\n**Project {project_base} will be copied to a new project: {project_wasteandmaterial}")
        bd.projects.set_current(project_base)
        bd.projects.copy_project(project_wasteandmaterial)

# %%% 1.1 Delete files from previous runs if you want

    if os.path.isdir(dir_data):
        redo = input("There is exiting output data, do you want to delete it? (y/n):  ")
    
        if redo == "y":
            shutil.rmtree(dir_data)
            print("\n** Data directory deleted\n")
        else:
            print("\n** Data directory will not be deleted")

    else:
        pass

# %%% 1.2 ExplodeDatabase.py
    """
    Open up EcoInvent db with wurst and save results as .pickle
    """

    ExplodeDatabase(project_base, project_wasteandmaterial, db_name)

# %%% 1.3.1 WasteSearch.py 
    '''
    run SearchWaste for the list of waste queries defined in config/queries_waste.py
    '''

    SearchWaste(db_name)

# %%% 1.3.2 SearchMaterial.py
    """
    run SearchMaterial for the list of materials defined 
    in config/list_materials.txt or from the default list 
    """
    SearchMaterial(project_wasteandmaterial, db_name)

# %%% 1.4 The rest of the custom functions
    '''
    calls from dbMakeCustom.py, ExchangeEditor.py, MethodEditor.py
    They do pretty much what their names suggest...
    '''

# makes an xlsx file from WasteSearch results in the database format needed for brightway2
    xl_filename = dbWriteExcel(project_wasteandmaterial, db_name, db_wasteandmaterial_name)

# imports the db_wasteandmaterial to the brightway project "WasteAndMaterialFootprint_<db_name>"
    dbExcel2BW(project_wasteandmaterial, db_wasteandmaterial_name, xl_filename)

# adds waste and material flows as elementary exchanges to each of the activities found
    ExchangeEditor(project_wasteandmaterial, db_name, db_wasteandmaterial_name)

# adds LCIA methods to for each of the waste and material categories defined above
    AddMethods(project_wasteandmaterial, db_wasteandmaterial_name)

    duration = (datetime.now() - start)
    print("\n*** Finished running WasteAndMaterialFootprint.\n\tDuration: " +
          str(duration).split(".")[0])
    print('*** Woah woah wee waa, great success!!')
    
# write the details of the run to a log file
    with open("data/tmp/main_log.txt", "a") as l:
        l.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\t Duration:" + str(duration).split(".")[0] +" "+ db_name+"\n")


# %% 2. RUN MAIN FUNCTION
# if __name__ == '__main__':
    
#     for args in args_list:
#         try:
#             WasteAndMaterialFootprint(args)
#         except Exception as e:
#             print(e)