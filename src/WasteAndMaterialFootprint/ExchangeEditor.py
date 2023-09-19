#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ExchangeEditor():
For every activity found by WasteAndMaterialSearch(), this function will add the relevant exchange from the db_wasteandmaterial.
This function takes the longest time to run (~10 min for each database).

Created on Thu Nov 17 15:30:24 2022

@author: SC-McD
based on the work of LL
"""

def ExchangeEditor(project_wasteandmaterial, db_name, db_wasteandmaterial_name):
    from tqdm import tqdm
    import os
    import pandas as pd
    import bw2data as bd
    from datetime import datetime
    
    bd.projects.set_current(project_wasteandmaterial)
    db = bd.Database(db_name)
    db_wasteandmaterial = bd.Database(db_wasteandmaterial_name)

    # find files produced by WasteAndMaterialSearch(), make df for each, add to a dictionary
    data = os.path.join(os.getcwd(), "../../data")
    tmp = os.path.join(data, "tmp")
    logs = os.path.join(data, "logs")
    search_results_path = os.path.join(
        os.getcwd(), "data/WasteSearchResults", db_name)
    file_dict = {}
    for f in os.listdir(search_results_path):
        f_path = os.path.join(search_results_path, f)
        if os.path.isfile(f_path) and f_path.endswith('.csv'):
            NAME = f.replace(".csv", '').replace(" ", "")
            df = pd.read_csv(f_path, sep=';', header=0, index_col=0)

            df.reset_index(inplace=True)
            df = df[["code", "name", "location", "ex_name",
                     "ex_amount", "ex_unit", "ex_location"]]
            file_dict.update({NAME: df})

 # Appending all processes with waste and material exchanges with custom biosphere waste and material exchanges 
 # in same amount and unit as technosphere waste and material exchange
    print("Appending waste and material exchanges as pseudo environmental flows in " + db_wasteandmaterial_name + " for the following categories:\n")
    countNAME = 0

    for NAME, df in file_dict.items():
        countNAME += 1
        start = datetime.now()
        progress_db = str(countNAME) + "/" + str(len(file_dict.items()))
        count = 0


    # get data for each exchange in the waste and material search results
        for exc in tqdm(df.to_dict('records'), desc=NAME + ": "):
            code = exc["code"]  
            name = exc["name"]
            location = exc["location"]
            ex_name = exc["ex_name"]
            amount = exc["ex_amount"]
            unit = exc["ex_unit"]
            ex_location = exc["ex_location"]
            process = db.get(code)
            wasteandmaterial_ex = db_wasteandmaterial.get(NAME)
            before = len(process.exchanges())
    
    # add a new exchange to the process
            process.new_exchange(
                input=wasteandmaterial_ex.key, amount=(amount), unit=unit, type='biosphere').save()
            after = len(process.exchanges())

    # count the added exchanges
            if (after-before) == 1:
                count += 1


    # add a log file entry
        end = datetime.now()
        duration = (end - start)

        log_entry = (end.strftime("%m/%d/%Y, %H:%M:%S")," ", db_name, NAME, "additions",
                     count, "duration:", str(duration))
        print(log_entry)
        log_file = os.path.join(tmp, 'ExchangeEditor.log')
        with open(log_file, 'a') as l:
            l.write(str(log_entry)+"\n")
