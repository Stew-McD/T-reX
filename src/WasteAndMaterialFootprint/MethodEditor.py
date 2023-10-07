#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module provides functions for adding, deleting, and checking methods related to waste and material footprints in a project.

Created on Sat Nov 19 12:21:04 2022
@author: Stew-McD
Based on the work of LL
"""

import bw2data as bd
from user_settings import project_wmf, db_wmf_name


def AddMethods():
    """
    Add methods to the specified project based on entries in the custom biosphere database.

    :param project_wmf: Name of the project.
    :param db_wmf_name: Name of the database.
    """
    print("\n*** Running AddMethods() ***\n")

    bd.projects.set_current(project_wmf)
    db_wmf = bd.Database(db_wmf_name)
    dic = db_wmf.load()
    sorted_items = sorted(dic.items())
    dic = dict(sorted_items)

    initial_method_count = len(bd.methods)

    for key, value in dic.items():
        m_unit = value["unit"]
        m_code = value["code"]
        m_name = (
            value["name"].replace("kilogram", "solid").replace("cubicmeter", "liquid")
        )
        m_type = value["type"]

        # Assign characterization factor based on type
        ch_factor = -1.0 if m_type == "waste" else 1.0

        if m_type == "waste":
            name_combined = "_".join((m_name.split("_")[0:2])) + "_combined"
            method_key = ("Waste Footprint", name_combined, m_name)
            description = "For estimating the waste footprint of an activity"
        else:
            method_key = (
                "Material Demand Footprint",
                m_name,
                m_name.split("_")[1].capitalize() + ' (demand)',
            )
            description = "For estimating the material footprint of an activity"

        m = bd.Method(method_key)
        
        count = 0
        if m in bd.methods:
            print(f"\t {str(method_key)} already exists")
            continue
            count += 1
        else:
            m.register(description=description, unit=m_unit)
            method_entry = [((db_wmf.name, m_code), ch_factor)]
            m.write(method_entry)

            print(f"\t {str(method_key)}")

    methods_added = len(bd.methods) - initial_method_count
    print("\n*** Added", methods_added, " new methods ***")

    return None


def DeleteMethods():
    """
    Delete methods associated with the "WasteAndMaterial Footprint" in the specified project.

    :param project_wmf: Name of the project.
    """

    bd.projects.set_current(project_wmf)

    initial_method_count = len(bd.methods)
    print("\nInitial # of methods:", initial_method_count, "\n")

    for m in list(bd.methods):
        if "WasteAndMaterial Footprint" in m:
            del bd.methods[m]
            print("Deleted:\t", m)

    final_method_count = len(bd.methods)
    print("\nFinal # of methods:", final_method_count)
    print("\n** Deleted {} methods".format(initial_method_count - final_method_count))

    return None


def CheckMethods():
    """
    Check methods associated with the "WasteAndMaterial Footprint" in the specified project.

    :param project_wmf: Name of the project.
    """

    bd.projects.set_current(project_wmf)

    methods_wasteandmaterial = [
        x for x in list(bd.methods) if "WasteAndMaterial Footprint" == x[0]
    ]

    for m in methods_wasteandmaterial:
        method = bd.Method(m)
        print(method.load())
        print(method.metadata)

    print(len(methods_wasteandmaterial))

    return None
