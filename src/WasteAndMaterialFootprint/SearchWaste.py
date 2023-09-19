#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is the second script of the WasteAndMaterialFootprint tool

SearchWaste() loads '<db name>_exploded.pickle', runs the search query, and produces a .csv to store the results (and a log entry).
The query is a dictionary that holds the variables NAME, CODE, and the search terms keywords_AND keywords_OR and keywords_NOT.
The format of the query dictionary is defined in config/queries_waste.py

Created on Wed Nov 16 15:09:03 2022

@author: SC-McD
based on the work of LL
"""

def SearchWaste():

    """
    This fuction loads '<db name>_exploded.pickle', runs the a set of search querys (which are defined in the config/queries_waste.py file), and produces .csvs to store the results (and a log entry).
    """

    import os
    from datetime import datetime
    import pandas as pd

    from user_settings import dir_searchwaste_results, dir_tmp, dir_logs
    from queries_waste import queries_waste

    db_name = queries_waste[0]["db_name"]
    
    dir_searchwaste_results = os.path.join(dir_searchwaste_results, db_name)

    if not os.path.exists(dir_searchwaste_results):
        os.makedirs(dir_searchwaste_results)

    # load exchanges into df from the dbExplode pickle file
    pickle_path = os.path.join(dir_tmp, db_name+ "_exploded.pickle")
    print("*** Loading pickle to dataframe...")
    df = pd.read_pickle(pickle_path)

    print("*** Searching for waste and material exchanges...")
    # this subfunction runs each individual search query in the set of queries

    def search(query):
        """
        This subfunction runs each individual search query in the set of queries which is a dictionary built by the config/queries_waste.py script

        Parameters
        ----------
        query : dict
        
        Returns
        -------
        A csv file with the results of the search query. This is saved in the data/SearchWasteResults/<db_name> folder with the name of the query.

        """
        # the variables are simplified here for the sake of readability
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
        wasteandmaterial_file = os.path.join(dir_searchwaste_results, wasteandmaterial_file_name)

        if df_results.shape[0] != 0:
            df_results.to_csv(wasteandmaterial_file+".csv", sep=";", )
            #df_results.to_html(wasteandmaterial_file+".html")

    # writes a log entry for each query
        log_entry = (
            "TIME: " + str(datetime.now()) +
            ", DB: " + query["db_name"] +
            ", RESULTS: "+str(df_results.shape[0]) +
            ", NAME: " + query["name"] +
            ", Search parameters" +
            ", AND=" + str(query["AND"]) +
            ", OR=" + str(query["OR"]) +
            ", NOT="+str(query["NOT"]) +
            ", UNIT=" + str(query['unit']) +
            ", CODE=" + str(CODE)
        )

        print("\n"+str(log_entry))
        date = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(dir_logs, f'SearchWaste_{date}.log')
        with open(log_file, 'a') as l:
            l.write(str(log_entry)+"\n")

    # calls the search function defined above for each query in the set of queries
    for query in queries_waste:
        search(query)
