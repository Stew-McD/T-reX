#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
|===============================================================|
| File: MakeCustomDatabase.py                                   |
| Project: WasteAndMaterialFootprint                            |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint   |
| Description: <<description>>                                  |
|---------------------------------------------------------------|
| File Created: Monday, 18th September 2023 11:21:13 am         |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                                |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Sunday, 24th September 2023 7:58:55 pm         |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|
"""
"""
This module contains functions for creating an xlsx representation of a Brightway2 database 
and importing it into Brightway2. 

Functions:
- dbWriteExcel: Creates an xlsx file representing a custom Brightway2 database.
- dbExcel2BW: Imports the custom database (created by dbWriteExcel) into Brightway2.
"""

from openpyxl import Workbook, load_workbook
import os
import bw2data as bd
import bw2io as bi
import glob

from user_settings import (
    dir_searchwaste_results,
    dir_searchmaterial_results,
    dir_databases_wasteandmaterial,
)


def get_files_from_tree(dir_searchmaterial_results, dir_searchwaste_results):
    # Get files in the SearchMaterial/*/grouped/ directory
    search_material_files = glob.glob(os.path.join(dir_searchmaterial_results, "*", "grouped", "*"))
    
    # Get files in the SearchWasteResults/* directory
    search_waste_files = glob.glob(os.path.join(dir_searchwaste_results, "*", "*"))
    
    all_files = search_material_files + search_waste_files

    # Extract only the filename without the suffix
    names = sorted(set(os.path.splitext(os.path.basename(file))[0] for file in all_files))
    
    return names

db_wmf_name = "WasteAndMaterialFootprint"
def dbWriteExcel(db_wmf_name):
    """
    Create an xlsx file representing a custom Brightway2 database.

    Parameters:
    - db_name (str): Name of the database.
    - db_wmf_name (str): Custom name for the Brightway2 database file.

    Returns:
    - str: Path to the generated xlsx file.
    """
        
    if not os.path.isdir(dir_databases_wasteandmaterial):
        os.makedirs(dir_databases_wasteandmaterial)

    xl_filename = dir_databases_wasteandmaterial / f"{db_wmf_name}.xlsx"

    # delete existing file if it exists
    if not os.path.isfile(xl_filename):

        # create new file and write header
        print(f"\n\n*** Writing custom database file: {db_wmf_name}\n")

        xl = Workbook()
        xl_db = xl.active
        xl_db["A1"] = "Database"
        xl_db["B1"] = db_wmf_name
        xl_db["A2"] = ""

    else:
        # open existing file and append to it
        print(f"\n\n*** Appending to existing custom database file: {db_wmf_name}\n")

        xl = load_workbook(xl_filename)
        xl_db = xl.active

    count = 0      
    names = get_files_from_tree(dir_searchmaterial_results, dir_searchwaste_results)
    for NAME in names:
        count += 1
        CODE = NAME
        UNIT = determine_unit_from_name(NAME)  
      
        if "waste" in NAME:
            TYPE = "waste"
        elif "Material" in NAME:
            TYPE = "material"
        else:
            TYPE = "?"

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
        xl_db.append([""])

    xl.save(xl_filename)
    print(
        f"\n ** Added {count} entries to the xlsx for the custom waste and material database:\n\t{db_wmf_name}"
    )

    return


def determine_unit_from_name(name):
    """
    Determine the unit based on the name.

    Parameters:
    - name (str): The name from which to infer the unit.

    Returns:
    - str: The inferred unit.
    """
    if "kilogram" in name:
        return "kilogram"
    elif "cubicmeter" in name or "water" in name or "gas" in name:
        return "cubic meter"
    elif "electricity" in name:
        return "kilowatt hour"
    elif "Material" in name:
        return "kilogram"
    else:
        return ""


def dbExcel2BW(project_wmf):
    """
    Import the custom database (created by dbWriteExcel) into Brightway2.

    Parameters:
    - project_wmf (str): Name of the Brightway2 project.
    - db_wmf_name (str): Name of the custom Brightway2 database.
    - xl_filename (str): Path to the xlsx file.

    Returns:
    - None
    """
    print(f"\n** Importing the custom database {db_wmf_name}**\n\t to the brightway2 project: {project_wmf}")

    xl_filename = dir_databases_wasteandmaterial / f"{db_wmf_name}.xlsx"
    bd.projects.set_current(project_wmf)

    if db_wmf_name not in bd.databases:
        # imports the custom database into BW2
        print("\n** Running BW2io ExcelImporter **\n")
        imp = bi.ExcelImporter(xl_filename)
        bi.create_core_migrations()  # needed to stop it from occasional crashing
        imp.apply_strategies()
        imp.statistics()
        imp.write_database()

        db_wmf = bd.Database(db_wmf_name)
        db_wmf.register()

        db_dict = db_wmf.metadata
        print("\n** Database metadata **")
        for key, value in db_dict.items():
            print(f"{key}: {value}")
            
    else:
        print(f"\n** Database {db_wmf_name} already exists **\n")
        db_wmf = bd.Database(db_wmf_name)
        imp = bi.ExcelImporter(xl_filename)
        
        for act in imp:
            if act['name'] not in db_wmf:
                print(f"\t Adding: \t{act['name']} to: \t {db_wmf_name}")
                db_wmf.new_activity(act)
            else:
                print(f"\t {act['name']} already exists in {db_wmf_name}")

        

    print("\n*** Great success! ***")

    return None
