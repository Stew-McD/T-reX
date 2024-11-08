"""
MethodEditor Module
===================

This module provides functions for adding, deleting, and checking methods related to waste and material footprints in a project.

Function Summary:
-----------------
- `AddMethods`: Adds new methods to a project based on a custom biosphere database.
- `DeleteMethods`: Removes specific methods from a project, particularly those related to waste and material footprints.
- `CheckMethods`: Lists and checks the methods in a project, focusing on those associated with waste and material footprints.
"""

import bw2data as bd
from config.user_settings import db_T_reX_name, project_T_reX


def AddMethods():
    """
    Add methods to the specified project based on entries in the custom biosphere database.

    :param project_T_reX: Name of the project.
    :param db_T_reX_name: Name of the database.
    """
    print("\n*** Running AddMethods() ***\n")

    bd.projects.set_current(project_T_reX)
    db_T_reX = bd.Database(db_T_reX_name)
    dic = db_T_reX.load()
    sorted_items = sorted(dic.items(), key=lambda item: item[1]["name"])
    dic = dict(sorted_items)

    initial_method_count = len(bd.methods)

    for key, value in dic.items():
        m_unit = value["unit"]
        m_code = value["code"]
        m_name = value["name"]
        m_type = value["type"]

        # Assign characterization factor based on type
        if m_type == "waste" and "carbon dioxide" not in m_name.lower():
            ch_factor = -1.0
        else:
            ch_factor = 1.0

        # Assign method key and description based on type
        if m_type == "waste":
            name_combined = m_code.split(" ")[0] + " combined"
            method_key = (
                "T-reX",
                "Waste: " + name_combined,
                m_code,
            )
            description = "For estimating the waste footprint of an activity"
        else:
            method_key = ("T-reX", "Demand: " + m_code, m_code)
            description = "For estimating the material demand footprint of an activity"

        m = bd.Method(method_key)

        if m in bd.methods:
            print(f"\t {str(method_key)} already exists")
            continue
        else:
            m.register(description=description, unit=m_unit)
            method_entry = [((db_T_reX.name, m_code), ch_factor)]
            m.write(method_entry)

            print(f"\t {str(method_key)}")

    methods_added = len(bd.methods) - initial_method_count
    print("\n*** Added", methods_added, " new methods ***")

    return None


def DeleteMethods():
    """
    Delete methods associated with the "WasteAndMaterial Footprint" in the specified project.

    :param project_T_reX: Name of the project.
    """

    bd.projects.set_current(project_T_reX)

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

    :param project_T_reX: Name of the project.
    """

    bd.projects.set_current(project_T_reX)

    methods_T_reX = [
        x for x in list(bd.methods) if "WasteAndMaterial Footprint" == x[0]
    ]

    for m in methods_T_reX:
        method = bd.Method(m)
        print(method.load())
        print(method.metadata)

    print(len(methods_T_reX))

    return None
