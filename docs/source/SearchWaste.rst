SearchWaste
===========

The SearchWaste module is a part of the T-reX tool, dedicated to processing waste-related data.
It loads data from a specified '< db name >_exploded.pickle' file, executes predefined search queries on this data,
and generates CSV files containing the results along with corresponding log entries. The search queries are
structured as dictionaries, specified in the `config/queries_waste.py` file, and include fields such as NAME,
CODE, and search terms like keywords_AND, keywords_OR, and keywords_NOT.

Functionality
-------------

The module provides the :func:`SearchWaste` function, which is responsible for three main actions:

1. Loading data from the '< db name >_exploded.pickle' file.

.. code-block:: python

      pickle_path = os.path.join(dir_tmp, db_name + "_exploded.pickle")
      df = pd.read_pickle(pickle_path)

2. Running the specified search queries on this data. These queries are designed to filter and identify
   relevant waste exchanges based on specific criteria.

   This functionality is implemented in the :func:`search` function, which is a subfunction of the :func:`SearchWaste` function.
   The :func:`search` function takes one argument, a search query from the list that is produced by the configuration module `queries_waste.py`.

   The search function is applied as follows, where `df` is the dataframe of the exploded database and `query` is a dictionary:

.. code-block:: python

    NAME_BASE = query["name"]
    UNIT = query["unit"]
    NAME = NAME_BASE + "-" + UNIT
    CODE = NAME.replace(" ", "")
    query.update({"code": NAME, "db_name": db_name})
    AND = query["AND"]
    OR = query["OR"]
    NOT = query["NOT"]
    DBNAME = query["db_name"]

    # Apply the search terms to the dataframe
    df_results = df[
        (df["ex_name"].apply(lambda x: all(i in x for i in AND)))
        & (df["ex_unit"] == UNIT)
        & (df["ex_amount"] != 0)
        # & (df["ex_amount"] != -1)
    ].copy()

    # Apply OR and NOT search filters
    if OR:
        df_results = df_results[
            df_results["ex_name"].apply(lambda x: any(i in x for i in OR))
        ]
    if NOT:
        df_results = df_results[
            df_results["ex_name"].apply(lambda x: not any(i in x for i in NOT))
        ]


3. Producing CSV files to store the results of these queries and creating log entries for each search operation. When customising the search configuration, it is important to check these files to see that the correct exchanges are being captured. The files are used by the subsequent modules to edit the exchanges and to produce LCIA methods.

Usage
-----

.. code-block:: python

    T-reX.SearchWaste(db_name, output_dir)


The :func:`SearchWaste` function is invoked with two arguments: the name of the Brightway2 database to be processed and the name of the directory to store the results. The search queries are specified in the `config/queries_waste.py` file. The function is designed for internal use within the T-reX tool and does not return a value but rather saves the output for subsequent use. It could be used separately, if you would have a .pickle file with exploded database as well as the config files in the right locations.
