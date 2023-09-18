#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*** This is the main function of the WasteAndMaterialFootprint tool ***

* To use the defaults, just run the whole script (but this will only work if you have the same format of project and database names)
* The terms of the search query can be edited in section 1.3 of this script
* The names of the projects and databases can be edited in section 2 of this script

DEFAULTS:

EI database is of form 'cutoff38' or 'con39'
* versions = ["35", "38", "39", "391]
* models = ["cutoff", 'con', 'apos']

The script will copy the project "default"+<db_name> to project "WasteAndMaterialFootprint"+<db_name>
* 'project_base': "default_"+<dbase>,
* 'project_wasteandmaterial': "WasteAndMaterialFootprint_"+<dbase>,


Created on Sat Nov 19 11:24:06 2022
@author: SC-McD
Based on the work of LL

"""
# %%% Imports
import shutil
from datetime import datetime
# custom modules
from dbExplode import dbExplode
from WasteAndMaterialFootprint.WasteAndMaterialSearch import WasteAndMaterialSearch
from dbMakeCustom import dbWriteExcel, dbExcel2BW
from ExchangeEditor import ExchangeEditor
from MethodEditor import AddMethods
# %% 1. DEFINE MAIN FUNCTION (EDIT YOUR SEARCH QUERY IN 1.3)


def WasteAndMaterialFootprint(args):

    print("\n*** Starting WasteAndMaterialFootprint ***\n")
    start = datetime.now()

# %%% 1.1 Define the project names and database names based on the arguments given
    project_base = args['project_base']
    project_wasteandmaterial = args['project_wasteandmaterial']
    db_name = args['db_name']
    db_wasteandmaterial_name = args['db_wasteandmaterial_name']

# %%% XX Delete files from previous runs if you want
    # #%%%% Clear program output directory: "tmp"
    # try:
    #     shutil.rmtree("data")
    #     print("tmp directory deleted\n")
    # except:
    #     print("tmp directory doesn't exist\n")

    # #%%%% Clear program output directory "WasteAndMaterialSearchResults"
    # try:
    #     shutil.rmtree("WasteAndMaterialSearchResults")
    #     print("WasteAndMaterialSearchResults directory deleted\n")
    # except:
    #     print("WasteAndMaterialSearchResults directory doesn't exist\n")

# %%% 1.2 dbExplode.py -
# Open up EcoInvent db with wurst and save results as .pickle
    print("\n*** Running dbExplode...")
    dbExplode(project_base, project_wasteandmaterial, db_name)

# %%% 1.3 WasteAndMaterialSearch.py -
# Define the search parameters here and run WasteAndMaterialSearch for each query (needs # to have .pickle already there from dbExplode)
# the terms should be either a string or a list of strings, as you find them

# set the names of the waste and material flow categories you want to search for
    names = ['digestion', 'hazardous', 'non_hazardous', "incineration",
             "open_burning", "recycling", "landfill", "composting", "total", 'radioactive']
# ! QUERY FORMAT
# setup the dictionary of search terms for each waste and material flow category
    queries_kg = []
    for name in names:
        query = {
            "db_name": db_name,
            "db_custom": db_wasteandmaterial_name,
            "name": "",
            "code": "",
            "unit": "kilogram",
            "AND": ["waste and material"],
            # if you replace "None" below, it must be with a with a
            # list of strings, like the other keywords have
            "OR": None,
            "NOT":  None
        }

# define here what the search parameters mean for each waste and material flow category
# if you want to customize the search parameters, you will
# likely need some trial and error to make sure you get what you want

        query.update({"name": "wasteandmaterial_"+name})
        if 'landfill' in name:
            query.update({"OR": ["landfill", "dumped", "deposit"]})
        if 'hazardous' == name:
            query.update({"OR": ["hazardous", "radioactive"]})
        if 'non_hazardous' == name:
            query.update({"NOT": ["hazardous", "radioactive"]})
        if 'incineration' in name:
            query["AND"] += ["incineration"]
        if 'open_burning' in name:
            query["AND"] += ["burning"]
        if 'recycling' in name:
            query["AND"] += ["recycling"]
        if 'composting' in name:
            query["AND"] += ["composting"]
        if 'digestion' in name:
            query["AND"] += ["digestion"]
        if 'radioactive' in name:
            query["AND"] += ["radioactive"]

# add the query to the list of queries
        queries_kg.append(query)

# add same queries defined above, now for liquid waste and material
    queries_m3 = []
    for q in queries_kg:
        q = q.copy()
        q.update({'unit': "cubic meter"})
        queries_m3.append(q)

    queries = queries_kg + queries_m3

# run WasteAndMaterialSearch for the list of queries
    WasteAndMaterialSearch(queries)

# %%% 1.4 The rest of the custom functions:
# calls from dbMakeCustom.py, ExchangeEditor.py, MethodEditor.py
# They do pretty much what their names suggest...

# makes an xlsx file from WasteAndMaterialSearch results in the database format needed for brightway2
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
if __name__ == '__main__':

# if you have a series of projects with a naming convention the same as this one, it is easy to run them all in a loop
# if not, you can edit the arguments in the list below to fit your naming convention or just run the function for a single project
    
    # simply comment out this section, edit the second last line of this script with the names of your project and database
    versions = ["39"] #"35", "38","39", 
    models = ["cutoff"] #, 'apos','con']
    dbases = ["{}{}".format(x, y) for x in models for y in versions]

    args_list = []
    for dbase in dbases:
        args = {'project_base': "default_"+dbase,
                'project_wasteandmaterial': "WasteAndMaterialFootprint_"+dbase,
                'db_name': dbase,
                'db_wasteandmaterial_name': "db_wasteandmaterial_"+dbase}
        args_list.append(args)
    
    for args in args_list:
        try:
            WasteAndMaterialFootprint(args)
        except Exception as e:
            print(e)
            
    # until here. 
    
    # now edit the args below to suit your naming conventions and and uncomment to run the function for a single project and database

    # args = {'project_base': "default_cutoff35", 'project_wasteandmaterial': "WasteAndMaterialFootprint_cutoff35", 'db_name': "cutoff35", 'db_wasteandmaterial_name': "db_wasteandmaterial_cutoff35"}
    # WasteAndMaterialFootprint(args)

