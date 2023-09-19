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

    search_results_path = os.path.join(os.getcwd(), "data/WasteAndMaterialSearchResults", db_name)

    xl_filename = os.path.join(search_results_path, "WasteAndMaterialSearchDatabase.xlsx")

# delete existing file if it exists
    if os.path.isfile(xl_filename):
        os.remove(xl_filename)

# create new file and write header
    print("\n\n*** Writing custom database file:", db_wasteandmaterial_name, "-->", xl_filename)
    xl = Workbook()
    xl_db = xl.active
    xl_db['A1'] = "Database"
    xl_db["B1"] = db_wasteandmaterial_name
    xl_db['A2'] = ''

# find files produced by WasteAndMaterialSearch(), and make a database entry for each
    count = 0
    for f in os.listdir(search_results_path):
        f_path = os.path.join(search_results_path, f)
        if os.path.isfile(f_path) and f_path.endswith('.csv'):
            count += 1
            NAME = f.replace(".csv", '').replace(" ", "")
            CODE = NAME
            if "kilogram" in NAME:
                UNIT = "kilogram"
            if "cubicmeter" in NAME:
                UNIT = "cubic meter"

# add a new activity to the custom database based on each search query (if there were results found)
            db_entry = {
                "Activity": NAME,
                "categories": "water, air, land",
                "code": CODE,
                "type": "emission",
                "unit": UNIT
            }

            print("Appending:", NAME)
            for key, value in db_entry.items():
                row = [key, str(value)]
                xl_db.append(row)

# BW2 ExcelImport requires an empty row between each activity
            xl_db.append([""])

    xl.save(xl_filename)
    print("Added", count, "entries to an xlsx for the custom waste and material db:", db_wasteandmaterial_name)

    return xl_filename

# %% dbExcel2BW

def dbExcel2BW(project_wasteandmaterial, db_wasteandmaterial_name, xl_filename):
    
    print("Importing to brightway2 project {} the custom database  {} produced by WasteAndMaterialSearch() and dbWriteExcel".format(
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
    print(db_wasteandmaterial.metadata)

    print("\nGreat success!")
