#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains functions for creating an xlsx representation of a Brightway2 database 
and importing it into Brightway2. 

Functions:
- dbWriteExcel: Creates an xlsx file representing a custom Brightway2 database.
- dbExcel2BW: Imports the custom database (created by dbWriteExcel) into Brightway2.
"""

from openpyxl import Workbook
import os
import bw2data as bd
import bw2io as bi

from user_settings import (
    dir_searchwaste_results,
    dir_searchmaterial_results,
    dir_databases_wasteandmaterial,
)


def dbWriteExcel(db_name, db_wasteandmaterial_name):
    """
    Create an xlsx file representing a custom Brightway2 database.

    Parameters:
    - db_name (str): Name of the database.
    - db_wasteandmaterial_name (str): Custom name for the Brightway2 database file.

    Returns:
    - str: Path to the generated xlsx file.
    """

    dir_searchwaste_results_db = dir_searchwaste_results / db_name
    dir_searchmaterial_results_grouped = (
        dir_searchmaterial_results / db_name / "grouped"
    )

    if not os.path.isdir(dir_databases_wasteandmaterial):
        os.makedirs(dir_databases_wasteandmaterial)

    xl_filename = dir_databases_wasteandmaterial / f"{db_wasteandmaterial_name}.xlsx"

    # delete existing file if it exists
    if os.path.isfile(xl_filename):
        os.remove(xl_filename)

    # create new file and write header
    print(f"\n\n*** Writing custom database file: {db_wasteandmaterial_name}\n")

    xl = Workbook()
    xl_db = xl.active
    xl_db["A1"] = "Database"
    xl_db["B1"] = db_wasteandmaterial_name
    xl_db["A2"] = ""

    count = 0
    files = os.listdir(dir_searchwaste_results_db) + os.listdir(
        dir_searchmaterial_results_grouped
    )

    for f in files:
        count += 1
        NAME = f.replace(".csv", "")
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
        f"\n ** Added {count} entries to the xlsx for the \
        custom waste and material db:\n{db_wasteandmaterial_name}"
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


def dbExcel2BW(project_wasteandmaterial, db_wasteandmaterial_name):
    """
    Import the custom database (created by dbWriteExcel) into Brightway2.

    Parameters:
    - project_wasteandmaterial (str): Name of the Brightway2 project.
    - db_wasteandmaterial_name (str): Name of the custom Brightway2 database.
    - xl_filename (str): Path to the xlsx file.

    Returns:
    - None
    """
    print(
        f"\n** Importing the custom database {db_wasteandmaterial_name}**\n**\
              to the brightway2 project {project_wasteandmaterial} **"
    )

    xl_filename = dir_databases_wasteandmaterial / f"{db_wasteandmaterial_name}.xlsx"
    bd.projects.set_current(project_wasteandmaterial)

    # imports the custom database into BW2
    print("\n** Running BW2io ExcelImporter **\n")
    imp = bi.ExcelImporter(xl_filename)
    bi.create_core_migrations()  # needed to stop it from occasional crashing
    imp.apply_strategies()
    imp.statistics()
    imp.write_database()

    db_wasteandmaterial_name = "db_wasteandmaterial_con391"
    db_wasteandmaterial = bd.Database(db_wasteandmaterial_name)
    db_wasteandmaterial.register()

    db_dict = db_wasteandmaterial.metadata
    print("\n** Database metadata **")
    for key, value in db_dict.items():
        print(f"{key}: {value}")

    print("\n*** Great success! ***")

    return None
