#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AddMethods() : Takes each entry in the custom biosphere database 'wasteandmaterial_db' and creates a new method from it.
Eg., ('WasteAndMaterial Footprint', 'wasteandmaterial_dumped_combined', wasteandmaterial_dumped_liquid)

Created on Sat Nov 19 12:21:04 2022

@author: SC-McD
based of the work of LL
"""

# add methods to the waste and material footprint project
def AddMethods(project_wasteandmaterial, db_wasteandmaterial_name):
    print("\n\n*** Adding new methods\n")
    import bw2data as bd

    bd.projects.set_current(project_wasteandmaterial)
    db_wasteandmaterial = bd.Database(db_wasteandmaterial_name)
    dic = db_wasteandmaterial.load()

    method_count = len(bd.methods)

    for key, value in dic.items():
        m_unit = value["unit"]
        m_code = value["code"]
        m_name = value["name"]
        m_name = m_name.replace("kilogram", "solid")
        m_name = m_name.replace("cubicmeter", "liquid")

# negative values for waste and material (to correct the fact that waste and material is considered a 'service' in LCA)
        ch_factor = -1.0

        name_combined = "_".join((m_name.split("_")[0:2])) + "_combined"
        method_key = ('WasteAndMaterial Footprint', name_combined, m_name)
        method_entry = [((db_wasteandmaterial.name, m_code), ch_factor)]

        m = bd.Method(method_key)
        m.register(description="For estimating the waste and material footprint of an activity (kg): ", unit=m_unit)
        m.write(method_entry)

        print('* Added: {}\t'.format(str(method_key)))

    methods_added = len(bd.methods) - method_count
    print("\n*** Added", methods_added, " new methods")

#If you want to delete methods, run this:
def DeleteMethods(project_wasteandmaterial) :

    import bw2data as bd
    bd.projects.set_current(project_wasteandmaterial)

    start = len(bd.methods)
    print("\n# of methods:", start,"\n")
    for m in list(bd.methods):
        if "WasteAndMaterial Footprint" in m:
            del bd.methods[m]
            print("deleted:\t", m)

    finish = len(bd.methods)
    print("\n# of methods :", finish)
    print("\n** Deleted {} methods".format(str(start - finish)))

# If you want to check if it worked, run this:
def CheckMethods(project_wasteandmaterial):
    import bw2data as bd
    bd.projects.set_current(project_wasteandmaterial)
    methods_wasteandmaterial = []
    for x in list(bd.methods):
        if "WasteAndMaterial Footprint" == x[0]:
            m = bd.Method(x)
            methods_wasteandmaterial.append(m)
            print(m.load())
            print(m.metadata)
    print(len(methods_wasteandmaterial))
