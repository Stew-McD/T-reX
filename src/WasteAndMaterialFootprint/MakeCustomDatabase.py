#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
There are two functions here:

* dbWriteExcel() : makes an xlsx file in the format of a Brightway2 database. For each .csv in the folder 'WasteAndMaterialSearchResults' a database entry will be added

* dbExcel2BW(): Takes the custom database produced by dbWriteExcel() and imports it into Brightway2. 
* Defaults: project = 'WasteAndMaterialFootprint_<db_name>', db = 'db_wasteandmaterial'

Created on Sat Nov 19 10:11:02 2022
@author: SC-McD
"""

def dbWriteExcel(project_wasteandmaterial, db_name, db_wasteandmaterial_name):
    
# setup xlsx file for custom database
    import os
    from openpyxl import Workbook

    from user_settings import dir_data, dir_tmp, dir_logs, dir_searchwaste_results, dir_searchmaterial_results, dir_databases_wasteandmaterial

    dir_searchwaste_results = dir_searchwaste_results / db_name
    dir_searchmaterial_results_grouped = dir_searchmaterial_results / db_name / 'grouped'
    
    if not os.path.isdir(dir_databases_wasteandmaterial): os.makedirs(dir_databases_wasteandmaterial)

    xl_filename = dir_databases_wasteandmaterial / (db_wasteandmaterial_name + ".xlsx")

# delete existing file if it exists
    if os.path.isfile(xl_filename):
        os.remove(xl_filename)

# create new file and write header
    print(f"\n\n*** Writing custom database file:       {db_wasteandmaterial_name} --> {xl_filename}\n")
    
    xl = Workbook()
    xl_db = xl.active
    xl_db['A1'] = "Database"
    xl_db["B1"] = db_wasteandmaterial_name
    xl_db['A2'] = ''

# find files produced by SearchWaste() and SearchMaterial(), and make a database entry for each
    count = 0

    files = os.listdir(dir_searchwaste_results) + os.listdir(dir_searchmaterial_results_grouped)
    
    for f in files:
        count += 1
        NAME = f.replace(".csv", '')
        CODE = NAME
        UNIT = ""
        if "kilogram" in NAME:
            UNIT = "kilogram"
        elif "cubicmeter" in NAME:
            UNIT = "cubic meter"
        elif 'electricity' in NAME:
            UNIT = 'kilowatt hour'
        elif 'water' in NAME or 'gas' in NAME:
            UNIT = 'cubic meter'
        
        if "Material" in NAME and UNIT == "":
            UNIT = 'kilogram'

        if 'waste' in NAME:
            TYPE = 'waste'
        elif 'Material' in NAME:
            TYPE = 'material'
        else:
            TYPE = '?'

# add a new activity to the custom database based on each search query (if there were results found)
        db_entry = {
            "Activity": NAME,
            "categories": "water, air, land",
            "code": CODE,
            "type": "emission",
            "unit": UNIT,
            "type": TYPE,
        }

        print("\t Appending:", NAME)
        for key, value in db_entry.items():
            row = [key, str(value)]
            xl_db.append(row)

# BW2 ExcelImport requires an empty row between each activity
        xl_db.append([""])

    xl.save(xl_filename)
    print(f"\n ** Added", count, f"entries to an xlsx for the custom waste and material db:{db_wasteandmaterial_name} ** \n")

    return xl_filename

# %% dbExcel2BW

def dbExcel2BW(project_wasteandmaterial, db_wasteandmaterial_name, xl_filename):
    
    print("Importing to brightway2 project {} the custom database  {} produced by WasteSearch()/MaterialSearch() and dbWriteExcel".format(
        project_wasteandmaterial, db_wasteandmaterial_name))
    
    import bw2data as bd
    import bw2io as bi
    from bw2io.migrations import create_core_migrations # not sure if this is needed

    xl_path = xl_filename
    bd.projects.set_current(project_wasteandmaterial)

# imports the custom database into BW2
    print("\nRunning BW2io ExcelImporter...\n")
    imp = bi.ExcelImporter(xl_path)
    create_core_migrations()
    imp.apply_strategies() # also may not be needed
    imp.statistics() 
    imp.write_database()

    db_wasteandmaterial = bd.Database(db_wasteandmaterial_name)
    db_wasteandmaterial.register()
    print(*db_wasteandmaterial.metadata, sep="\n")

    print("\nGreat success!")
