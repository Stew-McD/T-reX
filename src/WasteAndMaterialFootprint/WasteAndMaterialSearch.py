#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the second script of the WasteAndMaterialFootprint tool

WasteAndMaterialSearch() loads '<db name>_exploded.pickle', runs the search query, and produces a .csv to store the results (and a log entry).
The query is a dictionary that holds the variables NAME, CODE, and the search terms keywords_AND keywords_OR and keywords_NOT.
The format of the query dictionary is in main.py. Edit the query with query.update[{ '<parameter>' : '<value>'}]

Created on Wed Nov 16 15:09:03 2022

@author: SC-McD
based on the work of LL
"""
# Defines the  waste and material search wrapper function which takes a set of queries as 
# an input and runs the search for each query with the subfunction search()
def WasteAndMaterialSearch(queries):
    import os
    import pandas as pd

    db_name = queries[0]["db_name"]
    search_results_path = os.path.join(
        os.getcwd(), 'data/WasteAndMaterialSearchResults', db_name)
    if not os.path.exists(search_results_path):
        os.makedirs(search_results_path)

    # load exchanges into df from the dbExplode pickle file
    tmp = os.path.join(os.getcwd(), "data/tmp")

    pickle_path = os.path.join(tmp, db_name+"_exploded.pickle")
    print("*** Loading pickle to dataframe...")
    df = pd.read_pickle(pickle_path)

    print("*** Searching for waste and material exchanges...")
    # this subfunction runs each individual search query in the set of queries

    def search(query):
        # the variables are simplified here for the sake of readability
        db_name = query["db_name"]
        NAME_BASE = query["name"]
        UNIT = query["unit"]
        NAME = NAME_BASE + "_" + UNIT
        CODE = NAME.replace(" ", "")
        query.update({"code": NAME})
        AND = query["AND"]
        OR = query["OR"]
        NOT = query["NOT"]

    # applies the search terms to the df
        df_results = df[
            (df["ex_name"].apply(lambda x: True if all(
                i in x for i in AND) else False))
            & (df["ex_unit"] == UNIT)
            & (df['ex_amount'] < 0)
            & (df["ex_amount"] != -1)
        ]

    # applies the OR and NOT search filters to the df
        if OR != None:
            df_results = df_results[(df_results["ex_name"].apply(
                lambda x: True if any(i in x for i in OR) else False))]

        if NOT != None:
            df_results = df_results[(df_results["ex_name"].apply(
                lambda x: False if any(i in x for i in NOT) else True))]

    # writes a csv file for each query
        wasteandmaterial_file_name = NAME.replace(" ", "")
        wasteandmaterial_file = os.path.join(search_results_path, wasteandmaterial_file_name)

        if df_results.shape[0] != 0:
            df_results.to_csv(wasteandmaterial_file+".csv", sep=";", )
            #df_results.to_html(wasteandmaterial_file+".html")

    # writes a log entry for each query
        log_entry = (
            " DB=" + query["db_name"] +
            " RESULTS="+str(df_results.shape[0]) +
            " NAME: " + query["name"] +
            ", Search parameters: AND=" + str(query["AND"]) +
            " OR=" + str(query["OR"]) +
            " NOT="+str(query["NOT"]) +
            " UNIT=" + str(query['unit']) +
            " CODE=" + str(CODE)
        )

        print("\n"+str(log_entry))
        log_file = os.path.join(tmp, 'WasteAndMaterialSearch.log')
        with open(log_file, 'a') as l:
            l.write(str(log_entry)+"\n")

    # calls the search function defined above for each query in the set of queries
    for query in queries:
        search(query)
