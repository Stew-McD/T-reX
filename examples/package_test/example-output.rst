.. code:: ipython3

    """
    main Module
    ===========
    
    Main module of the `T-reX` tool.
    
    This script serves as the entry point for the `T-reX` tool. It orchestrates the overall process, including the setup and execution of various subprocesses like database explosion, material and waste searches, and the editing of exchanges. 
    
    The script supports both single and multiple project/database modes, as well as the option to use multiprocessing. It also facilitates the use of the premise module to generate future scenario databases.
    
    Customisation:
    --------------
    - Project and database names, and other settings can be edited in `config/user_settings.py`.
    - Waste search query terms can be customised in `config/queries_waste.py`.
    - The list of materials can be modified in `config/queries_materials.py`.
    
    Usage:
    ------
    To use the default settings, run the script with `python main.py`. 
    Arguments can be provided to change project/database names or to delete the project before running.
    
    """
    
    
    #  0. Imports and configuration
    
    # Import standard modules
    import os
    import sys
    from time import sleep
    from datetime import datetime
    from multiprocessing import Pool, cpu_count
    from pathlib import Path
    import bw2data as bd
    
    
    # not necessary (but fun), so in a try/except block
    try:
        import cowsay
        import logging
    
        logging.getLogger("playsound").setLevel(logging.ERROR)
        from playsound import playsound
    except ImportError:
        pass
    
    # If running on a cluster, get the number of CPUs available
    num_cpus = int(
        os.environ.get(
            "SLURM_CPUS_PER_TASK", os.environ.get("SLURM_JOB_CPUS_PER_NODE", cpu_count())
        )
    )
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    # # Set the working directory to the location of this script
    # os.chdir(script_dir)
    # sys.path.insert(0, str(cwd))
    
    # # Add the config dir to the Python path
    # dir_config = cwd / "config"
    
    # sys.path.insert(0, str(dir_config))
    
    # import custom modules (from root dir)
    from ExchangeEditor import ExchangeEditor
    from ExplodeDatabase import ExplodeDatabase
    from FutureScenarios import MakeFutureScenarios
    from MakeCustomDatabase import dbExcel2BW, dbWriteExcel
    from MethodEditor import AddMethods
    from SearchMaterial import SearchMaterial
    from SearchWaste import SearchWaste
    from VerifyDatabase import VerifyDatabase
    
    # import configuration from config/user_settings.py
    from config.user_settings import (
        custom_bw2_dir,
        db_T_reX_name,
        delete_T_reX_project,
        dir_logs,
        dir_tmp,
        dir_config,
        generate_args_list,
        project_base,
        project_premise,
        project_T_reX,
        use_multiprocessing,
        use_premise,
        use_T_reX,
        do_search,
        do_methods,
        do_edit,
        single_database,
    )
    
    # Check from the settings if a custom datadir is declared
    if custom_bw2_dir:
        os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir
    
    
    # 1. DEFINE MAIN FUNCTION: T-reX()
    def run():
        """
        Main function serving as the wrapper for the T-reX tool.
    
        This function coordinates the various components of the tool, including:
            creating future scenario databases,
            setting up and processing each database for T-reX footprinting,
            and combining results into a custom database.
            adding LCIA methods to the project for each of the waste/material flows.
    
        The function supports various modes of operation based on the settings in `config/user_settings.py`.
        Specifications for material and waste searches can be customised in `queries_materials`.
        """
        print(
            f"""
        {80*'='}
        {80*'~'}
        {'** Starting the T-reX tool **'.center(80, ' ')}
        {80*'~'}
        {80*'='}
        """
        )
        # create future scenario databases
        if use_premise:
            MakeFutureScenarios()
    
        assert use_T_reX, "use_T_reX is False, so T-reX will not run"
    
        start_time = datetime.now()
        args_list = generate_args_list(single_database=single_database)
        total_databases = len(args_list)
        all_databases = list(set(bd.databases) - {"biosphere3"})
    
        print(
            f"\nStarting T-reX for {total_databases}/{len(all_databases)} databases in project {project_base}\n{'-'*50}"
        )
        for arg in args_list:
            print(f"\t{arg['db_name']}")
    
        # Make new project, delete previous project if you want to start over, or use existing project
        bd.projects.purge_deleted_directories()
        if project_T_reX in bd.projects and delete_T_reX_project:
            print(f"\n* Deleting previous project {project_T_reX}")
            bd.projects.delete_project(project_T_reX, True)
            bd.projects.purge_deleted_directories()
    
        if project_T_reX in bd.projects:
            print(f"* WasteAndMaterial project already exists: {project_T_reX}")
            bd.projects.set_current(project_T_reX)
    
        if project_T_reX not in bd.projects:
            print(
                f"\n* Project {project_base} will be copied to a new project: {project_T_reX}"
            )
            bd.projects.set_current(project_base)
            bd.projects.copy_project(project_T_reX)
            bd.projects.set_current(project_T_reX)
    
        # 1.1 Run the initial steps for each database in the project
        def process_db_setup(args, db_number, total_databases):
            """
            Process initial setup for a given database within the project.
    
            This function is responsible for setting up each database by running the ExplodeAndSearch process.
            It handles any exceptions during the process and logs errors.
    
            :param dict args: Arguments containing database and project settings.
            :param int db_number: The current database number in the processing sequence.
            :param int total_databases: Total number of databases to be processed.
            :return: int: Returns 1 if successful, 0 if an error occurred.
            """
            print(f'\n{"-"*80}')
            try:
                print(
                    f"\n** Pre-processing database ({db_number+1}/{total_databases}): {args['db_name']}**\n"
                )
                print(args)
                if do_search:
                    ExplodeAndSearch(args)
                print(f'\n{"-"*80}')
                return 1  # successfully processed
            except Exception as e:
                print(
                    f"\n{'@'*50}\n\tError pre-processing database {args['db_name']}! \n\n\t{e}\n{'@'*50}\n"
                )
                print(f'\n{"-"*80}')
                return 0  # error occurred
    
        results = []
        if use_multiprocessing:
            with Pool(processes=num_cpus) as pool:
                for db_number, arg in enumerate(args_list):
                    pool.apply_async(
                        process_db_setup,
                        (arg, db_number, total_databases),
                        callback=results.append,
                    )
    
        else:
            for db_number, arg in enumerate(args_list):
                result = process_db_setup(arg, db_number, total_databases)
                results.append(result)
    
        successful_count = sum(results)
    
        end_time = datetime.now()
        duration = end_time - start_time
    
        if do_methods:
            #  1.2 MakeCustomDatabase.py: Make the custom database from the combined search results
            dbWriteExcel()
            dbExcel2BW()
            #  1.3 MethodEditor.py: adds LCIA methods to the project for each of the waste/material flows
            AddMethods()
    
        print(
            f"""
        {80*'-'}
        *** Preprocessing completed ***
    
        \t Total databases:          {total_databases}
        \t Successfully processed:   {successful_count}
        \t Duration:                 {str(duration).split('.')[0]} (h:m:s)
        {80*'-'}
        
        """
        )
    
        def process_db(args, db_number, total_databases):
            """
            Process the database by editing exchanges
    
            :param dict args: Arguments containing database and project settings.
            :param int db_number: The current database number in the processing sequence.
            :param int total_databases: Total number of databases to be processed.
    
            :return: int: Returns 1 if successful, 0 if an error occurred.
            """
            print(f'\n{"-"*80}')
            try:
                print(
                    f"\n** Processing database ({db_number}/{total_databases}): {args['db_name']}**"
                )
                print("Arguments:")
                print(args)
                if do_edit:
                    EditExchanges(args)
                print(f'{"-"*80}\n')
                return 1  # successfully processed
            except Exception as e:
                print(
                    f"\n{'@'*50}\n\tError processing database {args['db_name']}! \n\n\t{e}\n{'@'*50}\n"
                )
                print(f'{"-"*80}\n')
                return 0  # error occurred
    
        results = []
        db_number = 0
        if use_multiprocessing:
            with Pool(processes=num_cpus) as pool:
                for arg in args_list:
                    pool.apply_async(
                        process_db,
                        (arg, db_number, total_databases),
                        callback=results.append,
                    )
    
        else:
            for args in args_list:
                db_number += 1
                result = process_db(args, db_number, total_databases)
                results.append(result)
    
        successful_count = sum(results)
    
        end_time = datetime.now()
        duration = end_time - start_time
    
        # 1.4 VerifyDatabase.py: Verify the database
        print(f'\n{"-"*80}')
        print("\t*** Verifying all databases in the project **")
        for arg in args_list:
            db_name = arg["db_name"]
            VerifyDatabase(project_T_reX, db_name)
            print(f'\n{"-"*80}\n')
    
        try:
            playsound(script_dir.parents[1] / "misc/success.mp3")
        except:
            pass
    
        print(
            f"""
        {80 * '~'}
        {80 * '='}
        {'T-reX Completed'.center(80, ' ')}
        {'~' * 80}
    
        Project:                  {project_T_reX}
        Total Databases:          {total_databases}
        Successfully Processed:   {successful_count}
        Duration:                 {str(duration).split('.')[0]} (h:m:s)
    
        {'=' * 80}
        {'~' * 80}
        """
        )
    
        sleep(1)
    
        try:
    
            def animate_cowsay(message, delay=0.2):
                cow = cowsay.get_output_string("cow", message)
                for line in cow.split("\n"):
                    print(line.center(80, " "))
                    sleep(delay)
                playsound(script_dir.parents[1] / "misc/moo.mp3")
    
            message = "\nLet's moooooo\n some LCA!\n"
            animate_cowsay(message)
        except:
            pass
    
        print(f'\n{"-"*80}\n')
        print(f'\n{"~"*80}\n')
        print(f'\n{"="*80}\n')
    
    
    def ExplodeAndSearch(args):
        """
        Exploding the database into separate exchanges, searching for waste and
        material flows, and processing these results.
    
        This includes:
            - ExplodeDatabase.py
            - SearchWaste.py
            - SearchMaterial.py
    
        :param args: Dictionary containing database and project settings.
        :returns: None
        """
    
        project_T_reX = args["project_T_reX"]
        db_name = args["db_name"]
    
        print(
            f"\n{'='*100}\n\t Starting T-reX for {db_name}\n{'='*100}"
        )
    
        # 1.2 Explode the database into separate exchanges
        existing_file = dir_tmp / (db_name + "_exploded.pickle")
        if os.path.isfile(existing_file):
            print(f"\n* Existing exploded database found: {existing_file}")
            print("\n* Existing data will be reused for the current run")
        else:
            ExplodeDatabase(db_name)
    
        # 1.3 Search the exploded database for T-reX flows
        SearchWaste(db_name)
        SearchMaterial(db_name, project_T_reX)
    
        return None
    
    
    def EditExchanges(args):
        """
        Edit exchanges in the database.
    
        This function adds T-reX flows to the activities and verifies the database.
    
        :param args: Dictionary containing database and project settings.
        :returns: None
        """
    
        db_name = args["db_name"]
        start = datetime.now()
        # Add T-reX flows to the activities, check that it worked
    
        ExchangeEditor(project_T_reX, db_name, db_T_reX_name)
        exit_code = VerifyDatabase(project_T_reX, db_name)
    
        if exit_code == 0:
            print("** Database verified successfully! **\n")
        else:
            print("** Error occurred during verification! **")
            print(f"\t Look in the logfile for details. exit_code = {exit_code}\n")
    
        # Final message and log
        duration = datetime.now() - start
        print(f"{'='*90}")
        print(
            f"\t*** Finished T-reX for {db_name} ***\n\t\t\tDuration: {str(duration).split('.')[0]} (h:m:s)"
        )
        print("\t*** Woah woah wee waa, great success!! ***")
        print(f"{'='*90}")
    
        with open(f"{dir_logs / 'main_log.txt'}", "a") as log:
            log.write(
                datetime.now().strftime("%Y-%m-%d")
                + "\t Duration:"
                + str(duration).split(".")[0]
                + " "
                + db_name
                + "\n"
            )
    
        return None
    
    
    # 2. RUN MAIN FUNCTION
    if __name__ == "__main__":
        run()


.. parsed-literal::

    Using environment variable BRIGHTWAY2_DIR for data directory:
    /home/stew/brightway2data
    
        ================================================================================
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                       ** Starting the T-reX tool **                
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ================================================================================
        
    *** Starting FutureScenarios.py ***
    	Using premise version (1, 8, 2, 'dev3')
    Deleted existing project SSP-cutoff_test
    Created new project SSP-cutoff_test from default
    
    ** Using: ecoinvent-3.9.1-cutoff**
    
    
     ** Processing scenario set 1 of 2, batch size 2 **
    
    //////////////////// EXTRACTING SOURCE DATABASE ////////////////////
    Cannot find cached database. Will create one now for next time...
    Getting activity data


.. parsed-literal::

    100%|██████████| 21238/21238 [00:00<00:00, 70870.17it/s]


.. parsed-literal::

    Adding exchange data to activities


.. parsed-literal::

    100%|██████████| 674593/674593 [00:19<00:00, 34835.68it/s]


.. parsed-literal::

    Filling out exchange data


.. parsed-literal::

    100%|██████████| 21238/21238 [00:01<00:00, 12262.49it/s]


.. parsed-literal::

    Set missing location of datasets to global scope.
    Set missing location of production exchanges to scope of dataset.
    Correct missing location of technosphere exchanges.
    Correct missing flow categories for biosphere exchanges
    Remove empty exchanges.
    Done!
    
    ////////////////// IMPORTING DEFAULT INVENTORIES ///////////////////
    Cannot find cached inventories. Will create them now for next time...
    Importing default inventories...
    
    Extracted 1 worksheets in 0.13 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Extracted 7 worksheets in 0.03 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.03 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.03 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Extracted 1 worksheets in 0.34 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    The following datasets to import already exist in the source database. They will not be imported
    +--------------------------------+--------------------------------+----------+-------------+
    |              Name              |       Reference product        | Location |     File    |
    +--------------------------------+--------------------------------+----------+-------------+
    | fluorspar production, 97% puri |     fluorspar, 97% purity      |   GLO    | lci-PV.xlsx |
    | metallization paste production | metallization paste, back side |   RER    | lci-PV.xlsx |
    | metallization paste production | metallization paste, back side |   RER    | lci-PV.xlsx |
    | metallization paste production | metallization paste, front sid |   RER    | lci-PV.xlsx |
    | photovoltaic module production | photovoltaic module, building- |   RER    | lci-PV.xlsx |
    | photovoltaic module production | photovoltaic module, building- |   RER    | lci-PV.xlsx |
    | photovoltaic mounting system p | photovoltaic mounting system,  |   RER    | lci-PV.xlsx |
    | photovoltaic mounting system p | photovoltaic mounting system,  |   RER    | lci-PV.xlsx |
    | photovoltaic mounting system p | photovoltaic mounting system,  |   RER    | lci-PV.xlsx |
    | photovoltaic panel factory con |   photovoltaic panel factory   |   GLO    | lci-PV.xlsx |
    |  polyvinylfluoride production  |       polyvinylfluoride        |    US    | lci-PV.xlsx |
    | polyvinylfluoride production,  | polyvinylfluoride, dispersion  |    US    | lci-PV.xlsx |
    | polyvinylfluoride, film produc |    polyvinylfluoride, film     |    US    | lci-PV.xlsx |
    | silicon production, metallurgi |  silicon, metallurgical grade  |    NO    | lci-PV.xlsx |
    |   vinyl fluoride production    |         vinyl fluoride         |    US    | lci-PV.xlsx |
    |   wafer factory construction   |         wafer factory          |    DE    | lci-PV.xlsx |
    +--------------------------------+--------------------------------+----------+-------------+
    Extracted 1 worksheets in 0.05 seconds
    Extracted 1 worksheets in 0.02 seconds
    Extracted 1 worksheets in 0.02 seconds
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    The following datasets to import already exist in the source database. They will not be imported
    +--------------------------------+--------------------------------+----------+--------------------------------+
    |              Name              |       Reference product        | Location |              File              |
    +--------------------------------+--------------------------------+----------+--------------------------------+
    | carbon dioxide, captured at ce | carbon dioxide, captured and r |   RER    | lci-synfuels-from-methanol-fro |
    +--------------------------------+--------------------------------+----------+--------------------------------+
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    The following datasets to import already exist in the source database. They will not be imported
    +--------------------------------+----------------------+----------+--------------------------------+
    |              Name              |  Reference product   | Location |              File              |
    +--------------------------------+----------------------+----------+--------------------------------+
    | methanol distillation, hydroge |  methanol, purified  |   RER    | lci-synfuels-from-methanol-fro |
    | methanol synthesis, hydrogen f | methanol, unpurified |   RER    | lci-synfuels-from-methanol-fro |
    +--------------------------------+----------------------+----------+--------------------------------+
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.00 seconds
    Extracted 1 worksheets in 0.01 seconds
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 5 worksheets in 0.67 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.03 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.06 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.03 seconds
    Extracted 1 worksheets in 0.01 seconds
    Extracted 2 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 0.02 seconds
    Extracted 1 worksheets in 0.02 seconds
    Extracted 1 worksheets in 0.01 seconds
    Extracted 1 worksheets in 0.04 seconds
    Extracted 1 worksheets in 0.02 seconds
    Extracted 1 worksheets in 0.01 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Data cached. It is advised to restart your workflow at this point.
    This allows premise to use the cached data instead, which results in
    a faster workflow.
    Done!
    
    /////////////////////// EXTRACTING IAM DATA ////////////////////////
    Done!
    `update_all()` will skip the following steps:
    update_two_wheelers(), update_cars(), and update_buses()
    If you want to update these steps, please run them separately afterwards.
    Extracted 1 worksheets in 5.47 seconds
    Extracted 1 worksheets in 5.47 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Vehicle fleet data is not available beyond 2050. Hence, 2050 is used as fleet year.
    Vehicle fleet data is not available beyond 2050. Hence, 2050 is used as fleet year.
    Anomalies found: check the change report.
    Done!
    Done!
    Error: "not all values found in index 'year'. Try setting the `method` keyword argument (example: method='nearest')."
    Write new database(s) to Brightway.
    Running all checks...
    Running all checks...
    Warning: No valid output stream.
    Title: Writing activities to SQLite3 database:
      Started: 12/30/2023 11:14:16
      Finished: 12/30/2023 11:14:40
      Total time elapsed: 00:00:24
      CPU %: 87.90
      Memory %: 29.08
    Created database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2065
    Warning: No valid output stream.
    Title: Writing activities to SQLite3 database:
      Started: 12/30/2023 11:15:43
      Finished: 12/30/2023 11:16:04
      Total time elapsed: 00:00:21
      CPU %: 99.00
      Memory %: 29.72
    Created database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2100
    Generate scenario report.
    Report saved under /home/stew/code/gh/T-reX/data/premise/export/scenario_report.
    Generate change report.
    Report saved under /home/stew/code/gh/T-reX/data/premise.
    
     ** Processing scenario set 2 of 2, batch size 2 **
    
    //////////////////// EXTRACTING SOURCE DATABASE ////////////////////
    Done!
    
    ////////////////// IMPORTING DEFAULT INVENTORIES ///////////////////
    Done!
    
    /////////////////////// EXTRACTING IAM DATA ////////////////////////
    Done!
    `update_all()` will skip the following steps:
    update_two_wheelers(), update_cars(), and update_buses()
    If you want to update these steps, please run them separately afterwards.
    Extracted 1 worksheets in 6.32 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Extracted 1 worksheets in 6.18 seconds
    Migrating to 3.8 first
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Applying strategy: migrate_datasets
    Applying strategy: migrate_exchanges
    Vehicle fleet data is not available beyond 2050. Hence, 2050 is used as fleet year.
    Vehicle fleet data is not available beyond 2050. Hence, 2050 is used as fleet year.
    Anomalies found: check the change report.
    Done!
    Done!
    Error: "not all values found in index 'year'. Try setting the `method` keyword argument (example: method='nearest')."
    Write new database(s) to Brightway.
    Running all checks...
    Running all checks...
    Warning: No valid output stream.
    Title: Writing activities to SQLite3 database:
      Started: 12/30/2023 11:23:11
      Finished: 12/30/2023 11:23:40
      Total time elapsed: 00:00:29
      CPU %: 94.90
      Memory %: 30.09
    Created database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065
    Warning: No valid output stream.
    Title: Writing activities to SQLite3 database:
      Started: 12/30/2023 11:24:55
      Finished: 12/30/2023 11:25:22
      Total time elapsed: 00:00:26
      CPU %: 98.70
      Memory %: 31.00
    Created database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100
    Generate scenario report.
    Report saved under /home/stew/code/gh/T-reX/data/premise/export/scenario_report.
    Generate change report.
    Report saved under /home/stew/code/gh/T-reX/data/premise.
    Adding ('IPCC 2021', 'climate change', 'GWP 20a, incl. H')
    Applying strategy: csv_restore_tuples
    Applying strategy: csv_numerize
    Applying strategy: csv_drop_unknown
    Applying strategy: set_biosphere_type
    Applying strategy: drop_unspecified_subcategories
    Applying strategy: link_iterable_by_fields
    Applying strategy: drop_falsey_uncertainty_fields_but_keep_zeros
    Applying strategy: convert_uncertainty_types_to_integers
    Applied 8 strategies in 0.07 seconds
    Wrote 1 LCIA methods with 248 characterization factors
    Adding ('IPCC 2021', 'climate change', 'GWP 100a, incl. H and bio CO2')
    Applying strategy: csv_restore_tuples
    Applying strategy: csv_numerize
    Applying strategy: csv_drop_unknown
    Applying strategy: set_biosphere_type
    Applying strategy: drop_unspecified_subcategories
    Applying strategy: link_iterable_by_fields
    Applying strategy: drop_falsey_uncertainty_fields_but_keep_zeros
    Applying strategy: convert_uncertainty_types_to_integers
    Applied 8 strategies in 0.07 seconds
    Wrote 1 LCIA methods with 255 characterization factors
    Adding ('IPCC 2021', 'climate change', 'GWP 20a, incl. H and bio CO2')
    Applying strategy: csv_restore_tuples
    Applying strategy: csv_numerize
    Applying strategy: csv_drop_unknown
    Applying strategy: set_biosphere_type
    Applying strategy: drop_unspecified_subcategories
    Applying strategy: link_iterable_by_fields
    Applying strategy: drop_falsey_uncertainty_fields_but_keep_zeros
    Applying strategy: convert_uncertainty_types_to_integers
    Applied 8 strategies in 0.07 seconds
    Wrote 1 LCIA methods with 255 characterization factors
    Adding ('IPCC 2021', 'climate change', 'GWP 100a, incl. H')
    Applying strategy: csv_restore_tuples
    Applying strategy: csv_numerize
    Applying strategy: csv_drop_unknown
    Applying strategy: set_biosphere_type
    Applying strategy: drop_unspecified_subcategories
    Applying strategy: link_iterable_by_fields
    Applying strategy: drop_falsey_uncertainty_fields_but_keep_zeros
    Applying strategy: convert_uncertainty_types_to_integers
    Applied 8 strategies in 0.07 seconds
    Wrote 1 LCIA methods with 248 characterization factors
    ***** Done! *****
    
    Starting T-reX for 5/5 databases in project SSP-cutoff_test
    --------------------------------------------------
    	ecoinvent-3.9.1-cutoff
    	ecoinvent_cutoff_3.9_remind_SSP2-Base_2065
    	ecoinvent_cutoff_3.9_remind_SSP2-Base_2100
    	ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065
    	ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100
    
    * Project SSP-cutoff_test will be copied to a new project: T_reXootprint-SSP-cutoff_test
    
    --------------------------------------------------------------------------------
    
    ** Pre-processing database (1/5): ecoinvent-3.9.1-cutoff**
    
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent-3.9.1-cutoff', 'db_T_reX_name': 'T-reX'}
    
    ====================================================================================================
    	 Starting T-reX for ecoinvent-3.9.1-cutoff
    ====================================================================================================
    
    *** Starting ExplodeDatabase ***
    ExplodeDatabase uses wurst to open a bw2 database, explodes the exchanges for each process, and then returns a pickle file with a DataFrame list of all activities
    
    ** db: ecoinvent-3.9.1-cutoff, in project: T_reXootprint-SSP-cutoff_test will be processed
    
    ** Opening the sausage...
    Getting activity data


.. parsed-literal::

    100%|██████████| 21238/21238 [00:00<00:00, 191491.58it/s]


.. parsed-literal::

    Adding exchange data to activities


.. parsed-literal::

    100%|██████████| 674593/674593 [00:30<00:00, 21777.78it/s]


.. parsed-literal::

    Filling out exchange data


.. parsed-literal::

    100%|██████████| 21238/21238 [00:01<00:00, 14409.99it/s]


.. parsed-literal::

    
    *** Extracting activities from db...
    
    *** Exploding exchanges from activities...
    
    *** Pickling...
    
     Pickle is: 51 MB
    
    *** The sausage <ecoinvent-3.9.1-cutoff> was exploded and pickled. Rejoice!
    
    *** Starting SearchWaste ***
    *** Loading pickle to dataframe ***
    *** Searching for waste exchanges ***
    	WasteFootprint_digestion  	| kilogram      	|      4
    	WasteFootprint_composting 	| kilogram      	|     26
    	WasteFootprint_open burning 	| kilogram      	|    535
    	WasteFootprint_incineration 	| kilogram      	|   1897
    	WasteFootprint_recycling  	| kilogram      	|    129
    	WasteFootprint_landfill   	| kilogram      	|   1430
    	WasteFootprint_hazardous  	| kilogram      	|   1842
    	WasteFootprint_carbon dioxide 	| kilogram      	|      0
    	WasteFootprint_total      	| kilogram      	|  28883
    	WasteFootprint_digestion  	| cubic meter   	|     16
    	WasteFootprint_composting 	| cubic meter   	|      0
    	WasteFootprint_open burning 	| cubic meter   	|      0
    	WasteFootprint_incineration 	| cubic meter   	|      2
    	WasteFootprint_recycling  	| cubic meter   	|      0
    	WasteFootprint_landfill   	| cubic meter   	|      2
    	WasteFootprint_hazardous  	| cubic meter   	|    423
    	WasteFootprint_carbon dioxide 	| cubic meter   	|      0
    	WasteFootprint_total      	| cubic meter   	|   3976
    *** Finished searching for waste exchanges ***
    
    *** Starting SearchMaterial ***
    *** Loading pickle to dataframe ***
    
    *** Loading activities 
    from database: ecoinvent-3.9.1-cutoff 
    in project: T_reXootprint-SSP-cutoff_test
    
    ** Materials (59) | (activity, group)
    	('market for aluminium', 'aluminium')
    	('market for antimony', 'antimony')
    	('market for bauxite', 'bauxite')
    	('market for beryllium', 'beryllium')
    	('market for bismuth', 'bismuth')
    	('market for cadmium', 'cadmium')
    	('market for calcium borates', 'borates')
    	('market for cement', 'cement')
    	('market for cerium', 'cerium')
    	('market for chromium', 'chromium')
    	('market for coal', 'coal')
    	('market for cobalt', 'cobalt')
    	('market for coke', 'coke')
    	('market for copper', 'copper')
    	('market for dysprosium', 'dysprosium')
    	('market for erbium', 'erbium')
    	('market for europium', 'europium')
    	('market for electricity,', 'electricity')
    	('market for ferroniobium,', 'niobium')
    	('market for fluorspar,', 'fluorspar')
    	('market for gadolinium', 'gadolinium')
    	('market for gallium', 'gallium')
    	('market for gold', 'gold')
    	('market for graphite', 'graphite')
    	('market for hafnium', 'hafnium')
    	('market for helium', 'helium')
    	('market for holmium', 'holmium')
    	('market for hydrogen,', 'hydrogen')
    	('market for indium', 'indium')
    	('market for latex', 'latex')
    	('market for lithium', 'lithium')
    	('market for magnesium', 'magnesium')
    	('market for natural gas,', 'natural gas')
    	('market for nickel', 'nickel')
    	('market for palladium', 'palladium')
    	('market for petroleum', 'petroleum')
    	('market for phosphate', 'phosphate rock')
    	('market for platinum', 'platinum')
    	('market for rare earth', 'rare earth')
    	('market for rhodium', 'rhodium')
    	('market for sand', 'sand')
    	('market for selenium', 'selenium')
    	('market for scandium', 'scandium')
    	('market for silicon', 'silicon')
    	('market for silver', 'silver')
    	('market for sodium borates', 'borates')
    	('market for strontium', 'strontium')
    	('market for tantalum', 'tantalum')
    	('market for tellurium', 'tellurium')
    	('market for tin', 'tin')
    	('market for titanium', 'titanium')
    	('market for uranium', 'uranium')
    	('market for tungsten', 'tungsten')
    	('market for vanadium', 'vanadium')
    	('market for vegetable oil,', 'vegetable oil')
    	('market for tap water', 'water')
    	('market for water,', 'water')
    	('market for zinc', 'zinc')
    	('market for zirconium', 'zirconium')
    
    * 1038 material markets were found:
                                                       name material_group  \
    89                     market for aluminium alloy, AlLi      aluminium   
    1023                  market for aluminium alloy, AlMg3      aluminium   
    80    market for aluminium alloy, metal matrix compo...      aluminium   
    239   market for aluminium around steel bi-metal str...      aluminium   
    496   market for aluminium around steel bi-metal wir...      aluminium   
    ...                                                 ...            ...   
    757                                market for zinc slag           zinc   
    476                             market for zinc sulfide           zinc   
    281                          market for zirconium oxide      zirconium   
    93           market for zirconium sponge, nuclear-grade      zirconium   
    107                  market for zirconium tetrachloride      zirconium   
    
         location  
    89        GLO  
    1023      GLO  
    80        GLO  
    239       GLO  
    496       GLO  
    ...       ...  
    757       GLO  
    476       GLO  
    281       GLO  
    93        GLO  
    107       GLO  
    
    [1038 rows x 3 columns]
    
    * Extracting classifications...
    
    
    Saved activities list to csv: 
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent-3.9.1-cutoff/material_activities.csv
    
    *** Searching for material exchanges in ecoinvent-3.9.1-cutoff ***
    
    *** Loading pickle to dataframe ***
    
    There were 50387 matching exchanges found in ecoinvent-3.9.1-cutoff
    
    Saved material exchanges to csv:
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent-3.9.1-cutoff/material_exchanges.csv
    
    *** Grouping material exchanges by material group 
    
    	  1822 : aluminium
    	    26 : antimony
    	    24 : bauxite
    	     1 : beryllium
    	    15 : borates
    	    17 : cadmium
    	  2575 : cement
    	     2 : cerium
    	   410 : chromium
    	   146 : coal
    	   166 : cobalt
    	    68 : coke
    	   915 : copper
    	     1 : dysprosium
    	 23823 : electricity
    	     1 : erbium
    	     1 : europium
    	    22 : fluorspar
    	     1 : gadolinium
    	     3 : gallium
    	    10 : gold
    	    30 : graphite
    	    43 : helium
    	     1 : holmium
    	   377 : hydrogen
    	    13 : indium
    	    49 : latex
    	    43 : lithium
    	   250 : magnesium
    	  5804 : natural gas
    	   342 : nickel
    	    22 : palladium
    	   503 : petroleum
    	   207 : phosphate rock
    	   164 : platinum
    	    37 : rare earth
    	    11 : rhodium
    	   553 : sand
    	     1 : scandium
    	     9 : selenium
    	   358 : silicon
    	    46 : silver
    	    27 : strontium
    	     3 : tantalum
    	     2 : tellurium
    	   103 : tin
    	   454 : titanium
    	     5 : tungsten
    	   136 : uranium
    	    34 : vegetable oil
    	 10145 : water
    	   557 : zinc
    	     9 : zirconium
    
    --------------------------------------------------------------------------------
    
    --------------------------------------------------------------------------------
    
    ** Pre-processing database (2/5): ecoinvent_cutoff_3.9_remind_SSP2-Base_2065**
    
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-Base_2065', 'db_T_reX_name': 'T-reX'}
    
    ====================================================================================================
    	 Starting T-reX for ecoinvent_cutoff_3.9_remind_SSP2-Base_2065
    ====================================================================================================
    
    *** Starting ExplodeDatabase ***
    ExplodeDatabase uses wurst to open a bw2 database, explodes the exchanges for each process, and then returns a pickle file with a DataFrame list of all activities
    
    ** db: ecoinvent_cutoff_3.9_remind_SSP2-Base_2065, in project: T_reXootprint-SSP-cutoff_test will be processed
    
    ** Opening the sausage...
    Getting activity data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:00<00:00, 205081.15it/s]


.. parsed-literal::

    Adding exchange data to activities


.. parsed-literal::

    100%|██████████| 692676/692676 [00:17<00:00, 39089.13it/s]


.. parsed-literal::

    Filling out exchange data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:01<00:00, 13914.56it/s]


.. parsed-literal::

    
    *** Extracting activities from db...
    
    *** Exploding exchanges from activities...
    
    *** Pickling...
    
     Pickle is: 52 MB
    
    *** The sausage <ecoinvent_cutoff_3.9_remind_SSP2-Base_2065> was exploded and pickled. Rejoice!
    
    *** Starting SearchWaste ***
    *** Loading pickle to dataframe ***
    *** Searching for waste exchanges ***
    	WasteFootprint_digestion  	| kilogram      	|      4
    	WasteFootprint_composting 	| kilogram      	|     26
    	WasteFootprint_open burning 	| kilogram      	|    535
    	WasteFootprint_incineration 	| kilogram      	|   2171
    	WasteFootprint_recycling  	| kilogram      	|    137
    	WasteFootprint_landfill   	| kilogram      	|   1530
    	WasteFootprint_hazardous  	| kilogram      	|   1928
    	WasteFootprint_carbon dioxide 	| kilogram      	|    119
    	WasteFootprint_total      	| kilogram      	|  29524
    	WasteFootprint_digestion  	| cubic meter   	|     16
    	WasteFootprint_composting 	| cubic meter   	|      0
    	WasteFootprint_open burning 	| cubic meter   	|      0
    	WasteFootprint_incineration 	| cubic meter   	|      2
    	WasteFootprint_recycling  	| cubic meter   	|      0
    	WasteFootprint_landfill   	| cubic meter   	|      2
    	WasteFootprint_hazardous  	| cubic meter   	|    437
    	WasteFootprint_carbon dioxide 	| cubic meter   	|      0
    	WasteFootprint_total      	| cubic meter   	|   4360
    *** Finished searching for waste exchanges ***
    
    *** Starting SearchMaterial ***
    *** Loading pickle to dataframe ***
    
    *** Loading activities 
    from database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2065 
    in project: T_reXootprint-SSP-cutoff_test
    
    ** Materials (59) | (activity, group)
    	('market for aluminium', 'aluminium')
    	('market for antimony', 'antimony')
    	('market for bauxite', 'bauxite')
    	('market for beryllium', 'beryllium')
    	('market for bismuth', 'bismuth')
    	('market for cadmium', 'cadmium')
    	('market for calcium borates', 'borates')
    	('market for cement', 'cement')
    	('market for cerium', 'cerium')
    	('market for chromium', 'chromium')
    	('market for coal', 'coal')
    	('market for cobalt', 'cobalt')
    	('market for coke', 'coke')
    	('market for copper', 'copper')
    	('market for dysprosium', 'dysprosium')
    	('market for erbium', 'erbium')
    	('market for europium', 'europium')
    	('market for electricity,', 'electricity')
    	('market for ferroniobium,', 'niobium')
    	('market for fluorspar,', 'fluorspar')
    	('market for gadolinium', 'gadolinium')
    	('market for gallium', 'gallium')
    	('market for gold', 'gold')
    	('market for graphite', 'graphite')
    	('market for hafnium', 'hafnium')
    	('market for helium', 'helium')
    	('market for holmium', 'holmium')
    	('market for hydrogen,', 'hydrogen')
    	('market for indium', 'indium')
    	('market for latex', 'latex')
    	('market for lithium', 'lithium')
    	('market for magnesium', 'magnesium')
    	('market for natural gas,', 'natural gas')
    	('market for nickel', 'nickel')
    	('market for palladium', 'palladium')
    	('market for petroleum', 'petroleum')
    	('market for phosphate', 'phosphate rock')
    	('market for platinum', 'platinum')
    	('market for rare earth', 'rare earth')
    	('market for rhodium', 'rhodium')
    	('market for sand', 'sand')
    	('market for selenium', 'selenium')
    	('market for scandium', 'scandium')
    	('market for silicon', 'silicon')
    	('market for silver', 'silver')
    	('market for sodium borates', 'borates')
    	('market for strontium', 'strontium')
    	('market for tantalum', 'tantalum')
    	('market for tellurium', 'tellurium')
    	('market for tin', 'tin')
    	('market for titanium', 'titanium')
    	('market for uranium', 'uranium')
    	('market for tungsten', 'tungsten')
    	('market for vanadium', 'vanadium')
    	('market for vegetable oil,', 'vegetable oil')
    	('market for tap water', 'water')
    	('market for water,', 'water')
    	('market for zinc', 'zinc')
    	('market for zirconium', 'zirconium')
    
    * 1041 material markets were found:
                                                      name material_group location
    416                   market for aluminium alloy, AlLi      aluminium      GLO
    201                  market for aluminium alloy, AlMg3      aluminium      GLO
    28   market for aluminium alloy, metal matrix compo...      aluminium      GLO
    944  market for aluminium around steel bi-metal str...      aluminium      GLO
    61   market for aluminium around steel bi-metal wir...      aluminium      GLO
    ..                                                 ...            ...      ...
    193                               market for zinc slag           zinc      GLO
    815                            market for zinc sulfide           zinc      GLO
    983                         market for zirconium oxide      zirconium      GLO
    811         market for zirconium sponge, nuclear-grade      zirconium      GLO
    356                 market for zirconium tetrachloride      zirconium      GLO
    
    [1041 rows x 3 columns]
    
    * Extracting classifications...
    
    	Error for activity: market for lithium carbonate, battery grade, classification: nan
    		Inferring from reference product base: "lithium carbonate", from reference product "lithium carbonate, battery grade"
    	Error for activity: market for lithium hydroxide, battery grade, classification: nan
    		Inferring from reference product base: "lithium hydroxide", from reference product "lithium hydroxide, battery grade"
    	Error for activity: market for graphite, battery grade, classification: nan
    		Inferring from reference product base: "graphite", from reference product "graphite, battery grade"
    
    Saved activities list to csv: 
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-Base_2065/material_activities.csv
    
    *** Searching for material exchanges in ecoinvent_cutoff_3.9_remind_SSP2-Base_2065 ***
    
    *** Loading pickle to dataframe ***
    
    There were 51396 matching exchanges found in ecoinvent_cutoff_3.9_remind_SSP2-Base_2065
    
    Saved material exchanges to csv:
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-Base_2065/material_exchanges.csv
    
    *** Grouping material exchanges by material group 
    
    	  1925 : aluminium
    	    26 : antimony
    	    24 : bauxite
    	     1 : beryllium
    	    15 : borates
    	    17 : cadmium
    	  2598 : cement
    	     3 : cerium
    	   425 : chromium
    	   146 : coal
    	   166 : cobalt
    	    71 : coke
    	  1064 : copper
    	     1 : dysprosium
    	 24074 : electricity
    	     1 : erbium
    	     1 : europium
    	    22 : fluorspar
    	     1 : gadolinium
    	     4 : gallium
    	    10 : gold
    	    33 : graphite
    	    46 : helium
    	     1 : holmium
    	   389 : hydrogen
    	    13 : indium
    	    50 : latex
    	    52 : lithium
    	   264 : magnesium
    	  5825 : natural gas
    	   369 : nickel
    	    23 : palladium
    	   503 : petroleum
    	   207 : phosphate rock
    	   170 : platinum
    	    37 : rare earth
    	    11 : rhodium
    	   560 : sand
    	     1 : scandium
    	     9 : selenium
    	   364 : silicon
    	    50 : silver
    	    28 : strontium
    	     3 : tantalum
    	     2 : tellurium
    	   111 : tin
    	   457 : titanium
    	     5 : tungsten
    	   140 : uranium
    	    37 : vegetable oil
    	 10438 : water
    	   592 : zinc
    	    11 : zirconium
    
    --------------------------------------------------------------------------------
    
    --------------------------------------------------------------------------------
    
    ** Pre-processing database (3/5): ecoinvent_cutoff_3.9_remind_SSP2-Base_2100**
    
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-Base_2100', 'db_T_reX_name': 'T-reX'}
    
    ====================================================================================================
    	 Starting T-reX for ecoinvent_cutoff_3.9_remind_SSP2-Base_2100
    ====================================================================================================
    
    *** Starting ExplodeDatabase ***
    ExplodeDatabase uses wurst to open a bw2 database, explodes the exchanges for each process, and then returns a pickle file with a DataFrame list of all activities
    
    ** db: ecoinvent_cutoff_3.9_remind_SSP2-Base_2100, in project: T_reXootprint-SSP-cutoff_test will be processed
    
    ** Opening the sausage...
    Getting activity data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:00<00:00, 220707.79it/s]


.. parsed-literal::

    Adding exchange data to activities


.. parsed-literal::

    100%|██████████| 692676/692676 [00:19<00:00, 35421.58it/s]


.. parsed-literal::

    Filling out exchange data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:01<00:00, 14697.41it/s]


.. parsed-literal::

    
    *** Extracting activities from db...
    
    *** Exploding exchanges from activities...
    
    *** Pickling...
    
     Pickle is: 52 MB
    
    *** The sausage <ecoinvent_cutoff_3.9_remind_SSP2-Base_2100> was exploded and pickled. Rejoice!
    
    *** Starting SearchWaste ***
    *** Loading pickle to dataframe ***
    *** Searching for waste exchanges ***
    	WasteFootprint_digestion  	| kilogram      	|      4
    	WasteFootprint_composting 	| kilogram      	|     26
    	WasteFootprint_open burning 	| kilogram      	|    535
    	WasteFootprint_incineration 	| kilogram      	|   2171
    	WasteFootprint_recycling  	| kilogram      	|    137
    	WasteFootprint_landfill   	| kilogram      	|   1530
    	WasteFootprint_hazardous  	| kilogram      	|   1928
    	WasteFootprint_carbon dioxide 	| kilogram      	|    119
    	WasteFootprint_total      	| kilogram      	|  29524
    	WasteFootprint_digestion  	| cubic meter   	|     16
    	WasteFootprint_composting 	| cubic meter   	|      0
    	WasteFootprint_open burning 	| cubic meter   	|      0
    	WasteFootprint_incineration 	| cubic meter   	|      2
    	WasteFootprint_recycling  	| cubic meter   	|      0
    	WasteFootprint_landfill   	| cubic meter   	|      2
    	WasteFootprint_hazardous  	| cubic meter   	|    437
    	WasteFootprint_carbon dioxide 	| cubic meter   	|      0
    	WasteFootprint_total      	| cubic meter   	|   4360
    *** Finished searching for waste exchanges ***
    
    *** Starting SearchMaterial ***
    *** Loading pickle to dataframe ***
    
    *** Loading activities 
    from database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2100 
    in project: T_reXootprint-SSP-cutoff_test
    
    ** Materials (59) | (activity, group)
    	('market for aluminium', 'aluminium')
    	('market for antimony', 'antimony')
    	('market for bauxite', 'bauxite')
    	('market for beryllium', 'beryllium')
    	('market for bismuth', 'bismuth')
    	('market for cadmium', 'cadmium')
    	('market for calcium borates', 'borates')
    	('market for cement', 'cement')
    	('market for cerium', 'cerium')
    	('market for chromium', 'chromium')
    	('market for coal', 'coal')
    	('market for cobalt', 'cobalt')
    	('market for coke', 'coke')
    	('market for copper', 'copper')
    	('market for dysprosium', 'dysprosium')
    	('market for erbium', 'erbium')
    	('market for europium', 'europium')
    	('market for electricity,', 'electricity')
    	('market for ferroniobium,', 'niobium')
    	('market for fluorspar,', 'fluorspar')
    	('market for gadolinium', 'gadolinium')
    	('market for gallium', 'gallium')
    	('market for gold', 'gold')
    	('market for graphite', 'graphite')
    	('market for hafnium', 'hafnium')
    	('market for helium', 'helium')
    	('market for holmium', 'holmium')
    	('market for hydrogen,', 'hydrogen')
    	('market for indium', 'indium')
    	('market for latex', 'latex')
    	('market for lithium', 'lithium')
    	('market for magnesium', 'magnesium')
    	('market for natural gas,', 'natural gas')
    	('market for nickel', 'nickel')
    	('market for palladium', 'palladium')
    	('market for petroleum', 'petroleum')
    	('market for phosphate', 'phosphate rock')
    	('market for platinum', 'platinum')
    	('market for rare earth', 'rare earth')
    	('market for rhodium', 'rhodium')
    	('market for sand', 'sand')
    	('market for selenium', 'selenium')
    	('market for scandium', 'scandium')
    	('market for silicon', 'silicon')
    	('market for silver', 'silver')
    	('market for sodium borates', 'borates')
    	('market for strontium', 'strontium')
    	('market for tantalum', 'tantalum')
    	('market for tellurium', 'tellurium')
    	('market for tin', 'tin')
    	('market for titanium', 'titanium')
    	('market for uranium', 'uranium')
    	('market for tungsten', 'tungsten')
    	('market for vanadium', 'vanadium')
    	('market for vegetable oil,', 'vegetable oil')
    	('market for tap water', 'water')
    	('market for water,', 'water')
    	('market for zinc', 'zinc')
    	('market for zirconium', 'zirconium')
    
    * 1041 material markets were found:
                                                      name material_group location
    523                   market for aluminium alloy, AlLi      aluminium      GLO
    219                  market for aluminium alloy, AlMg3      aluminium      GLO
    729  market for aluminium alloy, metal matrix compo...      aluminium      GLO
    907  market for aluminium around steel bi-metal str...      aluminium      GLO
    656  market for aluminium around steel bi-metal wir...      aluminium      GLO
    ..                                                 ...            ...      ...
    200                               market for zinc slag           zinc      GLO
    879                            market for zinc sulfide           zinc      GLO
    373                         market for zirconium oxide      zirconium      GLO
    166         market for zirconium sponge, nuclear-grade      zirconium      GLO
    273                 market for zirconium tetrachloride      zirconium      GLO
    
    [1041 rows x 3 columns]
    
    * Extracting classifications...
    
    	Error for activity: market for graphite, battery grade, classification: nan
    		Inferring from reference product base: "graphite", from reference product "graphite, battery grade"
    	Error for activity: market for lithium hydroxide, battery grade, classification: nan
    		Inferring from reference product base: "lithium hydroxide", from reference product "lithium hydroxide, battery grade"
    	Error for activity: market for lithium carbonate, battery grade, classification: nan
    		Inferring from reference product base: "lithium carbonate", from reference product "lithium carbonate, battery grade"
    
    Saved activities list to csv: 
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-Base_2100/material_activities.csv
    
    *** Searching for material exchanges in ecoinvent_cutoff_3.9_remind_SSP2-Base_2100 ***
    
    *** Loading pickle to dataframe ***
    
    There were 51396 matching exchanges found in ecoinvent_cutoff_3.9_remind_SSP2-Base_2100
    
    Saved material exchanges to csv:
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-Base_2100/material_exchanges.csv
    
    *** Grouping material exchanges by material group 
    
    	  1925 : aluminium
    	    26 : antimony
    	    24 : bauxite
    	     1 : beryllium
    	    15 : borates
    	    17 : cadmium
    	  2598 : cement
    	     3 : cerium
    	   425 : chromium
    	   146 : coal
    	   166 : cobalt
    	    71 : coke
    	  1064 : copper
    	     1 : dysprosium
    	 24074 : electricity
    	     1 : erbium
    	     1 : europium
    	    22 : fluorspar
    	     1 : gadolinium
    	     4 : gallium
    	    10 : gold
    	    33 : graphite
    	    46 : helium
    	     1 : holmium
    	   389 : hydrogen
    	    13 : indium
    	    50 : latex
    	    52 : lithium
    	   264 : magnesium
    	  5825 : natural gas
    	   369 : nickel
    	    23 : palladium
    	   503 : petroleum
    	   207 : phosphate rock
    	   170 : platinum
    	    37 : rare earth
    	    11 : rhodium
    	   560 : sand
    	     1 : scandium
    	     9 : selenium
    	   364 : silicon
    	    50 : silver
    	    28 : strontium
    	     3 : tantalum
    	     2 : tellurium
    	   111 : tin
    	   457 : titanium
    	     5 : tungsten
    	   140 : uranium
    	    37 : vegetable oil
    	 10438 : water
    	   592 : zinc
    	    11 : zirconium
    
    --------------------------------------------------------------------------------
    
    --------------------------------------------------------------------------------
    
    ** Pre-processing database (4/5): ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065**
    
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065', 'db_T_reX_name': 'T-reX'}
    
    ====================================================================================================
    	 Starting T-reX for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065
    ====================================================================================================
    
    *** Starting ExplodeDatabase ***
    ExplodeDatabase uses wurst to open a bw2 database, explodes the exchanges for each process, and then returns a pickle file with a DataFrame list of all activities
    
    ** db: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065, in project: T_reXootprint-SSP-cutoff_test will be processed
    
    ** Opening the sausage...
    Getting activity data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:00<00:00, 28568.53it/s]


.. parsed-literal::

    Adding exchange data to activities


.. parsed-literal::

    100%|██████████| 692676/692676 [00:22<00:00, 30689.12it/s]


.. parsed-literal::

    Filling out exchange data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:01<00:00, 13019.77it/s]


.. parsed-literal::

    
    *** Extracting activities from db...
    
    *** Exploding exchanges from activities...
    
    *** Pickling...
    
     Pickle is: 52 MB
    
    *** The sausage <ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065> was exploded and pickled. Rejoice!
    
    *** Starting SearchWaste ***
    *** Loading pickle to dataframe ***
    *** Searching for waste exchanges ***
    	WasteFootprint_digestion  	| kilogram      	|      4
    	WasteFootprint_composting 	| kilogram      	|     26
    	WasteFootprint_open burning 	| kilogram      	|    535
    	WasteFootprint_incineration 	| kilogram      	|   2171
    	WasteFootprint_recycling  	| kilogram      	|    137
    	WasteFootprint_landfill   	| kilogram      	|   1530
    	WasteFootprint_hazardous  	| kilogram      	|   1928
    	WasteFootprint_carbon dioxide 	| kilogram      	|    119
    	WasteFootprint_total      	| kilogram      	|  29524
    	WasteFootprint_digestion  	| cubic meter   	|     16
    	WasteFootprint_composting 	| cubic meter   	|      0
    	WasteFootprint_open burning 	| cubic meter   	|      0
    	WasteFootprint_incineration 	| cubic meter   	|      2
    	WasteFootprint_recycling  	| cubic meter   	|      0
    	WasteFootprint_landfill   	| cubic meter   	|      2
    	WasteFootprint_hazardous  	| cubic meter   	|    437
    	WasteFootprint_carbon dioxide 	| cubic meter   	|      0
    	WasteFootprint_total      	| cubic meter   	|   4360
    *** Finished searching for waste exchanges ***
    
    *** Starting SearchMaterial ***
    *** Loading pickle to dataframe ***
    
    *** Loading activities 
    from database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065 
    in project: T_reXootprint-SSP-cutoff_test
    
    ** Materials (59) | (activity, group)
    	('market for aluminium', 'aluminium')
    	('market for antimony', 'antimony')
    	('market for bauxite', 'bauxite')
    	('market for beryllium', 'beryllium')
    	('market for bismuth', 'bismuth')
    	('market for cadmium', 'cadmium')
    	('market for calcium borates', 'borates')
    	('market for cement', 'cement')
    	('market for cerium', 'cerium')
    	('market for chromium', 'chromium')
    	('market for coal', 'coal')
    	('market for cobalt', 'cobalt')
    	('market for coke', 'coke')
    	('market for copper', 'copper')
    	('market for dysprosium', 'dysprosium')
    	('market for erbium', 'erbium')
    	('market for europium', 'europium')
    	('market for electricity,', 'electricity')
    	('market for ferroniobium,', 'niobium')
    	('market for fluorspar,', 'fluorspar')
    	('market for gadolinium', 'gadolinium')
    	('market for gallium', 'gallium')
    	('market for gold', 'gold')
    	('market for graphite', 'graphite')
    	('market for hafnium', 'hafnium')
    	('market for helium', 'helium')
    	('market for holmium', 'holmium')
    	('market for hydrogen,', 'hydrogen')
    	('market for indium', 'indium')
    	('market for latex', 'latex')
    	('market for lithium', 'lithium')
    	('market for magnesium', 'magnesium')
    	('market for natural gas,', 'natural gas')
    	('market for nickel', 'nickel')
    	('market for palladium', 'palladium')
    	('market for petroleum', 'petroleum')
    	('market for phosphate', 'phosphate rock')
    	('market for platinum', 'platinum')
    	('market for rare earth', 'rare earth')
    	('market for rhodium', 'rhodium')
    	('market for sand', 'sand')
    	('market for selenium', 'selenium')
    	('market for scandium', 'scandium')
    	('market for silicon', 'silicon')
    	('market for silver', 'silver')
    	('market for sodium borates', 'borates')
    	('market for strontium', 'strontium')
    	('market for tantalum', 'tantalum')
    	('market for tellurium', 'tellurium')
    	('market for tin', 'tin')
    	('market for titanium', 'titanium')
    	('market for uranium', 'uranium')
    	('market for tungsten', 'tungsten')
    	('market for vanadium', 'vanadium')
    	('market for vegetable oil,', 'vegetable oil')
    	('market for tap water', 'water')
    	('market for water,', 'water')
    	('market for zinc', 'zinc')
    	('market for zirconium', 'zirconium')
    
    * 1041 material markets were found:
                                                       name material_group  \
    830                    market for aluminium alloy, AlLi      aluminium   
    608                   market for aluminium alloy, AlMg3      aluminium   
    850   market for aluminium alloy, metal matrix compo...      aluminium   
    1009  market for aluminium around steel bi-metal str...      aluminium   
    73    market for aluminium around steel bi-metal wir...      aluminium   
    ...                                                 ...            ...   
    218                                market for zinc slag           zinc   
    282                             market for zinc sulfide           zinc   
    571                          market for zirconium oxide      zirconium   
    537          market for zirconium sponge, nuclear-grade      zirconium   
    168                  market for zirconium tetrachloride      zirconium   
    
         location  
    830       GLO  
    608       GLO  
    850       GLO  
    1009      GLO  
    73        GLO  
    ...       ...  
    218       GLO  
    282       GLO  
    571       GLO  
    537       GLO  
    168       GLO  
    
    [1041 rows x 3 columns]
    
    * Extracting classifications...
    
    	Error for activity: market for graphite, battery grade, classification: nan
    		Inferring from reference product base: "graphite", from reference product "graphite, battery grade"
    	Error for activity: market for lithium hydroxide, battery grade, classification: nan
    		Inferring from reference product base: "lithium hydroxide", from reference product "lithium hydroxide, battery grade"
    	Error for activity: market for lithium carbonate, battery grade, classification: nan
    		Inferring from reference product base: "lithium carbonate", from reference product "lithium carbonate, battery grade"
    
    Saved activities list to csv: 
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065/material_activities.csv
    
    *** Searching for material exchanges in ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065 ***
    
    *** Loading pickle to dataframe ***
    
    There were 51396 matching exchanges found in ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065
    
    Saved material exchanges to csv:
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065/material_exchanges.csv
    
    *** Grouping material exchanges by material group 
    
    	  1925 : aluminium
    	    26 : antimony
    	    24 : bauxite
    	     1 : beryllium
    	    15 : borates
    	    17 : cadmium
    	  2598 : cement
    	     3 : cerium
    	   425 : chromium
    	   146 : coal
    	   166 : cobalt
    	    71 : coke
    	  1064 : copper
    	     1 : dysprosium
    	 24074 : electricity
    	     1 : erbium
    	     1 : europium
    	    22 : fluorspar
    	     1 : gadolinium
    	     4 : gallium
    	    10 : gold
    	    33 : graphite
    	    46 : helium
    	     1 : holmium
    	   389 : hydrogen
    	    13 : indium
    	    50 : latex
    	    52 : lithium
    	   264 : magnesium
    	  5825 : natural gas
    	   369 : nickel
    	    23 : palladium
    	   503 : petroleum
    	   207 : phosphate rock
    	   170 : platinum
    	    37 : rare earth
    	    11 : rhodium
    	   560 : sand
    	     1 : scandium
    	     9 : selenium
    	   364 : silicon
    	    50 : silver
    	    28 : strontium
    	     3 : tantalum
    	     2 : tellurium
    	   111 : tin
    	   457 : titanium
    	     5 : tungsten
    	   140 : uranium
    	    37 : vegetable oil
    	 10438 : water
    	   592 : zinc
    	    11 : zirconium
    
    --------------------------------------------------------------------------------
    
    --------------------------------------------------------------------------------
    
    ** Pre-processing database (5/5): ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100**
    
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100', 'db_T_reX_name': 'T-reX'}
    
    ====================================================================================================
    	 Starting T-reX for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100
    ====================================================================================================
    
    *** Starting ExplodeDatabase ***
    ExplodeDatabase uses wurst to open a bw2 database, explodes the exchanges for each process, and then returns a pickle file with a DataFrame list of all activities
    
    ** db: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100, in project: T_reXootprint-SSP-cutoff_test will be processed
    
    ** Opening the sausage...
    Getting activity data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:00<00:00, 169095.50it/s]


.. parsed-literal::

    Adding exchange data to activities


.. parsed-literal::

    100%|██████████| 692676/692676 [00:23<00:00, 29821.18it/s]


.. parsed-literal::

    Filling out exchange data


.. parsed-literal::

    100%|██████████| 22433/22433 [00:01<00:00, 14191.14it/s]


.. parsed-literal::

    
    *** Extracting activities from db...
    
    *** Exploding exchanges from activities...
    
    *** Pickling...
    
     Pickle is: 52 MB
    
    *** The sausage <ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100> was exploded and pickled. Rejoice!
    
    *** Starting SearchWaste ***
    *** Loading pickle to dataframe ***
    *** Searching for waste exchanges ***
    	WasteFootprint_digestion  	| kilogram      	|      4
    	WasteFootprint_composting 	| kilogram      	|     26
    	WasteFootprint_open burning 	| kilogram      	|    535
    	WasteFootprint_incineration 	| kilogram      	|   2171
    	WasteFootprint_recycling  	| kilogram      	|    137
    	WasteFootprint_landfill   	| kilogram      	|   1530
    	WasteFootprint_hazardous  	| kilogram      	|   1928
    	WasteFootprint_carbon dioxide 	| kilogram      	|    119
    	WasteFootprint_total      	| kilogram      	|  29524
    	WasteFootprint_digestion  	| cubic meter   	|     16
    	WasteFootprint_composting 	| cubic meter   	|      0
    	WasteFootprint_open burning 	| cubic meter   	|      0
    	WasteFootprint_incineration 	| cubic meter   	|      2
    	WasteFootprint_recycling  	| cubic meter   	|      0
    	WasteFootprint_landfill   	| cubic meter   	|      2
    	WasteFootprint_hazardous  	| cubic meter   	|    437
    	WasteFootprint_carbon dioxide 	| cubic meter   	|      0
    	WasteFootprint_total      	| cubic meter   	|   4360
    *** Finished searching for waste exchanges ***
    
    *** Starting SearchMaterial ***
    *** Loading pickle to dataframe ***
    
    *** Loading activities 
    from database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100 
    in project: T_reXootprint-SSP-cutoff_test
    
    ** Materials (59) | (activity, group)
    	('market for aluminium', 'aluminium')
    	('market for antimony', 'antimony')
    	('market for bauxite', 'bauxite')
    	('market for beryllium', 'beryllium')
    	('market for bismuth', 'bismuth')
    	('market for cadmium', 'cadmium')
    	('market for calcium borates', 'borates')
    	('market for cement', 'cement')
    	('market for cerium', 'cerium')
    	('market for chromium', 'chromium')
    	('market for coal', 'coal')
    	('market for cobalt', 'cobalt')
    	('market for coke', 'coke')
    	('market for copper', 'copper')
    	('market for dysprosium', 'dysprosium')
    	('market for erbium', 'erbium')
    	('market for europium', 'europium')
    	('market for electricity,', 'electricity')
    	('market for ferroniobium,', 'niobium')
    	('market for fluorspar,', 'fluorspar')
    	('market for gadolinium', 'gadolinium')
    	('market for gallium', 'gallium')
    	('market for gold', 'gold')
    	('market for graphite', 'graphite')
    	('market for hafnium', 'hafnium')
    	('market for helium', 'helium')
    	('market for holmium', 'holmium')
    	('market for hydrogen,', 'hydrogen')
    	('market for indium', 'indium')
    	('market for latex', 'latex')
    	('market for lithium', 'lithium')
    	('market for magnesium', 'magnesium')
    	('market for natural gas,', 'natural gas')
    	('market for nickel', 'nickel')
    	('market for palladium', 'palladium')
    	('market for petroleum', 'petroleum')
    	('market for phosphate', 'phosphate rock')
    	('market for platinum', 'platinum')
    	('market for rare earth', 'rare earth')
    	('market for rhodium', 'rhodium')
    	('market for sand', 'sand')
    	('market for selenium', 'selenium')
    	('market for scandium', 'scandium')
    	('market for silicon', 'silicon')
    	('market for silver', 'silver')
    	('market for sodium borates', 'borates')
    	('market for strontium', 'strontium')
    	('market for tantalum', 'tantalum')
    	('market for tellurium', 'tellurium')
    	('market for tin', 'tin')
    	('market for titanium', 'titanium')
    	('market for uranium', 'uranium')
    	('market for tungsten', 'tungsten')
    	('market for vanadium', 'vanadium')
    	('market for vegetable oil,', 'vegetable oil')
    	('market for tap water', 'water')
    	('market for water,', 'water')
    	('market for zinc', 'zinc')
    	('market for zirconium', 'zirconium')
    
    * 1041 material markets were found:
                                                      name material_group location
    232                   market for aluminium alloy, AlLi      aluminium      GLO
    898                  market for aluminium alloy, AlMg3      aluminium      GLO
    873  market for aluminium alloy, metal matrix compo...      aluminium      GLO
    757  market for aluminium around steel bi-metal str...      aluminium      GLO
    0    market for aluminium around steel bi-metal wir...      aluminium      GLO
    ..                                                 ...            ...      ...
    673                               market for zinc slag           zinc      GLO
    91                             market for zinc sulfide           zinc      GLO
    864                         market for zirconium oxide      zirconium      GLO
    468         market for zirconium sponge, nuclear-grade      zirconium      GLO
    941                 market for zirconium tetrachloride      zirconium      GLO
    
    [1041 rows x 3 columns]
    
    * Extracting classifications...
    
    	Error for activity: market for lithium carbonate, battery grade, classification: nan
    		Inferring from reference product base: "lithium carbonate", from reference product "lithium carbonate, battery grade"
    	Error for activity: market for graphite, battery grade, classification: nan
    		Inferring from reference product base: "graphite", from reference product "graphite, battery grade"
    	Error for activity: market for lithium hydroxide, battery grade, classification: nan
    		Inferring from reference product base: "lithium hydroxide", from reference product "lithium hydroxide, battery grade"
    
    Saved activities list to csv: 
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100/material_activities.csv
    
    *** Searching for material exchanges in ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100 ***
    
    *** Loading pickle to dataframe ***
    
    There were 51396 matching exchanges found in ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100
    
    Saved material exchanges to csv:
    /home/stew/code/gh/T-reX/data/SearchMaterialResults/ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100/material_exchanges.csv
    
    *** Grouping material exchanges by material group 
    
    	  1925 : aluminium
    	    26 : antimony
    	    24 : bauxite
    	     1 : beryllium
    	    15 : borates
    	    17 : cadmium
    	  2598 : cement
    	     3 : cerium
    	   425 : chromium
    	   146 : coal
    	   166 : cobalt
    	    71 : coke
    	  1064 : copper
    	     1 : dysprosium
    	 24074 : electricity
    	     1 : erbium
    	     1 : europium
    	    22 : fluorspar
    	     1 : gadolinium
    	     4 : gallium
    	    10 : gold
    	    33 : graphite
    	    46 : helium
    	     1 : holmium
    	   389 : hydrogen
    	    13 : indium
    	    50 : latex
    	    52 : lithium
    	   264 : magnesium
    	  5825 : natural gas
    	   369 : nickel
    	    23 : palladium
    	   503 : petroleum
    	   207 : phosphate rock
    	   170 : platinum
    	    37 : rare earth
    	    11 : rhodium
    	   560 : sand
    	     1 : scandium
    	     9 : selenium
    	   364 : silicon
    	    50 : silver
    	    28 : strontium
    	     3 : tantalum
    	     2 : tellurium
    	   111 : tin
    	   457 : titanium
    	     5 : tungsten
    	   140 : uranium
    	    37 : vegetable oil
    	 10438 : water
    	   592 : zinc
    	    11 : zirconium
    
    --------------------------------------------------------------------------------
    
    
    *** Writing custom database file: T-reX
    
    
    
    *** Appending to existing custom database file: T-reX
    
    	 Appending: MaterialFootprint_aluminium
    	 Appending: MaterialFootprint_antimony
    	 Appending: MaterialFootprint_bauxite
    	 Appending: MaterialFootprint_beryllium
    	 Appending: MaterialFootprint_borates
    	 Appending: MaterialFootprint_cadmium
    	 Appending: MaterialFootprint_cement
    	 Appending: MaterialFootprint_cerium
    	 Appending: MaterialFootprint_chromium
    	 Appending: MaterialFootprint_coal
    	 Appending: MaterialFootprint_cobalt
    	 Appending: MaterialFootprint_coke
    	 Appending: MaterialFootprint_copper
    	 Appending: MaterialFootprint_dysprosium
    	 Appending: MaterialFootprint_electricity
    	 Appending: MaterialFootprint_erbium
    	 Appending: MaterialFootprint_europium
    	 Appending: MaterialFootprint_fluorspar
    	 Appending: MaterialFootprint_gadolinium
    	 Appending: MaterialFootprint_gallium
    	 Appending: MaterialFootprint_gold
    	 Appending: MaterialFootprint_graphite
    	 Appending: MaterialFootprint_helium
    	 Appending: MaterialFootprint_holmium
    	 Appending: MaterialFootprint_hydrogen
    	 Appending: MaterialFootprint_indium
    	 Appending: MaterialFootprint_latex
    	 Appending: MaterialFootprint_lithium
    	 Appending: MaterialFootprint_magnesium
    	 Appending: MaterialFootprint_natural gas
    	 Appending: MaterialFootprint_nickel
    	 Appending: MaterialFootprint_palladium
    	 Appending: MaterialFootprint_petroleum
    	 Appending: MaterialFootprint_phosphate rock
    	 Appending: MaterialFootprint_platinum
    	 Appending: MaterialFootprint_rare earth
    	 Appending: MaterialFootprint_rhodium
    	 Appending: MaterialFootprint_sand
    	 Appending: MaterialFootprint_scandium
    	 Appending: MaterialFootprint_selenium
    	 Appending: MaterialFootprint_silicon
    	 Appending: MaterialFootprint_silver
    	 Appending: MaterialFootprint_strontium
    	 Appending: MaterialFootprint_tantalum
    	 Appending: MaterialFootprint_tellurium
    	 Appending: MaterialFootprint_tin
    	 Appending: MaterialFootprint_titanium
    	 Appending: MaterialFootprint_tungsten
    	 Appending: MaterialFootprint_uranium
    	 Appending: MaterialFootprint_vegetable oil
    	 Appending: MaterialFootprint_water
    	 Appending: MaterialFootprint_zinc
    	 Appending: MaterialFootprint_zirconium
    	 Appending: WasteFootprint_carbondioxide-kilogram
    	 Appending: WasteFootprint_composting-kilogram
    	 Appending: WasteFootprint_digestion-cubicmeter
    	 Appending: WasteFootprint_digestion-kilogram
    	 Appending: WasteFootprint_hazardous-cubicmeter
    	 Appending: WasteFootprint_hazardous-kilogram
    	 Appending: WasteFootprint_incineration-cubicmeter
    	 Appending: WasteFootprint_incineration-kilogram
    	 Appending: WasteFootprint_landfill-cubicmeter
    	 Appending: WasteFootprint_landfill-kilogram
    	 Appending: WasteFootprint_openburning-kilogram
    	 Appending: WasteFootprint_recycling-kilogram
    	 Appending: WasteFootprint_total-cubicmeter
    	 Appending: WasteFootprint_total-kilogram
    
     ** Added 67 entries to the xlsx for the custom T-reX database:
    	T-reX
    
    ** Importing the custom database T-reX**
    	 to the brightway2 project: T_reXootprint-SSP-cutoff_test
    
    ** Running BW2io ExcelImporter **
    
    Extracted 1 worksheets in 0.01 seconds
    Applying strategy: csv_restore_tuples
    Applying strategy: csv_restore_booleans
    Applying strategy: csv_numerize
    Applying strategy: csv_drop_unknown
    Applying strategy: csv_add_missing_exchanges_section
    Applying strategy: normalize_units
    Applying strategy: normalize_biosphere_categories
    Applying strategy: normalize_biosphere_names
    Applying strategy: strip_biosphere_exc_locations
    Applying strategy: set_code_by_activity_hash
    Applying strategy: link_iterable_by_fields
    Applying strategy: assign_only_product_as_production
    Applying strategy: link_technosphere_by_activity_hash
    Applying strategy: drop_falsey_uncertainty_fields_but_keep_zeros
    Applying strategy: convert_uncertainty_types_to_integers
    Applying strategy: convert_activity_parameters_to_list
    Applied 16 strategies in 3.88 seconds
    67 datasets
    0 exchanges
    0 unlinked exchanges
      
    Warning: No valid output stream.
    Title: Writing activities to SQLite3 database:
      Started: 12/30/2023 11:31:14
      Finished: 12/30/2023 11:31:14
      Total time elapsed: 00:00:00
      CPU %: 0.00
      Memory %: 35.15
    Created database: T-reX
    
    ** Database metadata **
    format: Excel
    depends: []
    backend: sqlite
    number: 67
    modified: 2023-12-30T11:31:14.732004
    searchable: True
    processed: 2023-12-30T11:31:14.925335
    
    *** Great success! ***
    
    *** Running AddMethods() ***
    
    	 ('T-reX', 'Demand: Aluminium', 'Aluminium')
    	 ('T-reX', 'Demand: Antimony', 'Antimony')
    	 ('T-reX', 'Demand: Bauxite', 'Bauxite')
    	 ('T-reX', 'Demand: Beryllium', 'Beryllium')
    	 ('T-reX', 'Demand: Borates', 'Borates')
    	 ('T-reX', 'Demand: Cadmium', 'Cadmium')
    	 ('T-reX', 'Demand: Cement', 'Cement')
    	 ('T-reX', 'Demand: Cerium', 'Cerium')
    	 ('T-reX', 'Demand: Chromium', 'Chromium')
    	 ('T-reX', 'Demand: Coal', 'Coal')
    	 ('T-reX', 'Demand: Cobalt', 'Cobalt')
    	 ('T-reX', 'Demand: Coke', 'Coke')
    	 ('T-reX', 'Demand: Copper', 'Copper')
    	 ('T-reX', 'Demand: Dysprosium', 'Dysprosium')
    	 ('T-reX', 'Demand: Electricity', 'Electricity')
    	 ('T-reX', 'Demand: Erbium', 'Erbium')
    	 ('T-reX', 'Demand: Europium', 'Europium')
    	 ('T-reX', 'Demand: Fluorspar', 'Fluorspar')
    	 ('T-reX', 'Demand: Gadolinium', 'Gadolinium')
    	 ('T-reX', 'Demand: Gallium', 'Gallium')
    	 ('T-reX', 'Demand: Gold', 'Gold')
    	 ('T-reX', 'Demand: Graphite', 'Graphite')
    	 ('T-reX', 'Demand: Helium', 'Helium')
    	 ('T-reX', 'Demand: Holmium', 'Holmium')
    	 ('T-reX', 'Demand: Hydrogen', 'Hydrogen')
    	 ('T-reX', 'Demand: Indium', 'Indium')
    	 ('T-reX', 'Demand: Latex', 'Latex')
    	 ('T-reX', 'Demand: Lithium', 'Lithium')
    	 ('T-reX', 'Demand: Magnesium', 'Magnesium')
    	 ('T-reX', 'Demand: Natural gas', 'Natural gas')
    	 ('T-reX', 'Demand: Nickel', 'Nickel')
    	 ('T-reX', 'Demand: Palladium', 'Palladium')
    	 ('T-reX', 'Demand: Petroleum', 'Petroleum')
    	 ('T-reX', 'Demand: Phosphate rock', 'Phosphate rock')
    	 ('T-reX', 'Demand: Platinum', 'Platinum')
    	 ('T-reX', 'Demand: Rare earth', 'Rare earth')
    	 ('T-reX', 'Demand: Rhodium', 'Rhodium')
    	 ('T-reX', 'Demand: Sand', 'Sand')
    	 ('T-reX', 'Demand: Scandium', 'Scandium')
    	 ('T-reX', 'Demand: Selenium', 'Selenium')
    	 ('T-reX', 'Demand: Silicon', 'Silicon')
    	 ('T-reX', 'Demand: Silver', 'Silver')
    	 ('T-reX', 'Demand: Strontium', 'Strontium')
    	 ('T-reX', 'Demand: Tantalum', 'Tantalum')
    	 ('T-reX', 'Demand: Tellurium', 'Tellurium')
    	 ('T-reX', 'Demand: Tin', 'Tin')
    	 ('T-reX', 'Demand: Titanium', 'Titanium')
    	 ('T-reX', 'Demand: Tungsten', 'Tungsten')
    	 ('T-reX', 'Demand: Uranium', 'Uranium')
    	 ('T-reX', 'Demand: Vegetable oil', 'Vegetable oil')
    	 ('T-reX', 'Demand: Water', 'Water')
    	 ('T-reX', 'Demand: Zinc', 'Zinc')
    	 ('T-reX', 'Demand: Zirconium', 'Zirconium')
    	 ('T-reX', 'Waste: Carbondioxide combined', 'Carbondioxide (kg)')
    	 ('T-reX', 'Waste: Composting combined', 'Composting (kg)')
    	 ('T-reX', 'Waste: Digestion combined', 'Digestion (m3)')
    	 ('T-reX', 'Waste: Digestion combined', 'Digestion (kg)')
    	 ('T-reX', 'Waste: Hazardous combined', 'Hazardous (m3)')
    	 ('T-reX', 'Waste: Hazardous combined', 'Hazardous (kg)')
    	 ('T-reX', 'Waste: Incineration combined', 'Incineration (m3)')
    	 ('T-reX', 'Waste: Incineration combined', 'Incineration (kg)')
    	 ('T-reX', 'Waste: Landfill combined', 'Landfill (m3)')
    	 ('T-reX', 'Waste: Landfill combined', 'Landfill (kg)')
    	 ('T-reX', 'Waste: Openburning combined', 'Openburning (kg)')
    	 ('T-reX', 'Waste: Recycling combined', 'Recycling (kg)')
    	 ('T-reX', 'Waste: Total combined', 'Total (m3)')
    	 ('T-reX', 'Waste: Total combined', 'Total (kg)')
    
    *** Added 67  new methods ***
    
        --------------------------------------------------------------------------------
        *** Preprocessing completed ***
    
        	 Total databases:          5
        	 Successfully processed:   5
        	 Duration:                 0:04:16 (h:m:s)
        --------------------------------------------------------------------------------
        
        
    
    --------------------------------------------------------------------------------
    
    ** Processing database (1/5): ecoinvent-3.9.1-cutoff**
    Arguments:
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent-3.9.1-cutoff', 'db_T_reX_name': 'T-reX'}
    
    
    *** ExchangeEditor() is running for ecoinvent-3.9.1-cutoff ***
    
    * Appending T-reX exchanges in T-reX
     


.. parsed-literal::

     -  1/66 : MaterialFootprint_aluminium                | [35m██████████████████████████████[0m | 100.0% | Progress:  1822 of 1822  | Elapsed: 00:23 | Remaining: 00:00
     -  2/66 : MaterialFootprint_antimony                 | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     -  3/66 : MaterialFootprint_bauxite                  | [35m██████████████████████████████[0m | 100.0% | Progress:    24 of 24    | Elapsed: 00:00 | Remaining: 00:00
     -  4/66 : MaterialFootprint_beryllium                | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     -  5/66 : MaterialFootprint_borates                  | [35m██████████████████████████████[0m | 100.0% | Progress:    15 of 15    | Elapsed: 00:00 | Remaining: 00:00
     -  6/66 : MaterialFootprint_cadmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    17 of 17    | Elapsed: 00:00 | Remaining: 00:00
     -  7/66 : MaterialFootprint_cement                   | [35m██████████████████████████████[0m | 100.0% | Progress:  2575 of 2575  | Elapsed: 00:28 | Remaining: 00:00
     -  8/66 : MaterialFootprint_cerium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     -  9/66 : MaterialFootprint_chromium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   410 of 410   | Elapsed: 00:04 | Remaining: 00:00
     - 10/66 : MaterialFootprint_coal                     | [35m██████████████████████████████[0m | 100.0% | Progress:   146 of 146   | Elapsed: 00:01 | Remaining: 00:00
     - 11/66 : MaterialFootprint_cobalt                   | [35m██████████████████████████████[0m | 100.0% | Progress:   166 of 166   | Elapsed: 00:01 | Remaining: 00:00
     - 12/66 : MaterialFootprint_coke                     | [35m██████████████████████████████[0m | 100.0% | Progress:    68 of 68    | Elapsed: 00:00 | Remaining: 00:00
     - 13/66 : MaterialFootprint_copper                   | [35m██████████████████████████████[0m | 100.0% | Progress:   915 of 915   | Elapsed: 00:10 | Remaining: 00:00
     - 14/66 : MaterialFootprint_dysprosium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 15/66 : MaterialFootprint_electricity              | [35m██████████████████████████████[0m | 100.0% | Progress: 23823 of 23823 | Elapsed: 04:16 | Remaining: 00:00
     - 16/66 : MaterialFootprint_erbium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 17/66 : MaterialFootprint_europium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 18/66 : MaterialFootprint_fluorspar                | [35m██████████████████████████████[0m | 100.0% | Progress:    22 of 22    | Elapsed: 00:00 | Remaining: 00:00
     - 19/66 : MaterialFootprint_gadolinium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 20/66 : MaterialFootprint_gallium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     - 21/66 : MaterialFootprint_gold                     | [35m██████████████████████████████[0m | 100.0% | Progress:    10 of 10    | Elapsed: 00:00 | Remaining: 00:00
     - 22/66 : MaterialFootprint_graphite                 | [35m██████████████████████████████[0m | 100.0% | Progress:    30 of 30    | Elapsed: 00:00 | Remaining: 00:00
     - 23/66 : MaterialFootprint_helium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    43 of 43    | Elapsed: 00:00 | Remaining: 00:00
     - 24/66 : MaterialFootprint_holmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 25/66 : MaterialFootprint_hydrogen                 | [35m██████████████████████████████[0m | 100.0% | Progress:   377 of 377   | Elapsed: 00:04 | Remaining: 00:00
     - 26/66 : MaterialFootprint_indium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    13 of 13    | Elapsed: 00:00 | Remaining: 00:00
     - 27/66 : MaterialFootprint_latex                    | [35m██████████████████████████████[0m | 100.0% | Progress:    49 of 49    | Elapsed: 00:00 | Remaining: 00:00
     - 28/66 : MaterialFootprint_lithium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    43 of 43    | Elapsed: 00:00 | Remaining: 00:00
     - 29/66 : MaterialFootprint_magnesium                | [35m██████████████████████████████[0m | 100.0% | Progress:   250 of 250   | Elapsed: 00:02 | Remaining: 00:00
     - 30/66 : MaterialFootprint_natural gas              | [35m██████████████████████████████[0m | 100.0% | Progress:  5804 of 5804  | Elapsed: 01:02 | Remaining: 00:00
     - 31/66 : MaterialFootprint_nickel                   | [35m██████████████████████████████[0m | 100.0% | Progress:   342 of 342   | Elapsed: 00:03 | Remaining: 00:00
     - 32/66 : MaterialFootprint_palladium                | [35m██████████████████████████████[0m | 100.0% | Progress:    22 of 22    | Elapsed: 00:00 | Remaining: 00:00
     - 33/66 : MaterialFootprint_petroleum                | [35m██████████████████████████████[0m | 100.0% | Progress:   503 of 503   | Elapsed: 00:05 | Remaining: 00:00
     - 34/66 : MaterialFootprint_phosphate rock           | [35m██████████████████████████████[0m | 100.0% | Progress:   207 of 207   | Elapsed: 00:02 | Remaining: 00:00
     - 35/66 : MaterialFootprint_platinum                 | [35m██████████████████████████████[0m | 100.0% | Progress:   164 of 164   | Elapsed: 00:01 | Remaining: 00:00
     - 36/66 : MaterialFootprint_rare earth               | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 37/66 : MaterialFootprint_rhodium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 38/66 : MaterialFootprint_sand                     | [35m██████████████████████████████[0m | 100.0% | Progress:   553 of 553   | Elapsed: 00:05 | Remaining: 00:00
     - 39/66 : MaterialFootprint_scandium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 40/66 : MaterialFootprint_selenium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     9 of 9     | Elapsed: 00:00 | Remaining: 00:00
     - 41/66 : MaterialFootprint_silicon                  | [35m██████████████████████████████[0m | 100.0% | Progress:   358 of 358   | Elapsed: 00:03 | Remaining: 00:00
     - 42/66 : MaterialFootprint_silver                   | [35m██████████████████████████████[0m | 100.0% | Progress:    46 of 46    | Elapsed: 00:00 | Remaining: 00:00
     - 43/66 : MaterialFootprint_strontium                | [35m██████████████████████████████[0m | 100.0% | Progress:    27 of 27    | Elapsed: 00:00 | Remaining: 00:00
     - 44/66 : MaterialFootprint_tantalum                 | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     - 45/66 : MaterialFootprint_tellurium                | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 46/66 : MaterialFootprint_tin                      | [35m██████████████████████████████[0m | 100.0% | Progress:   103 of 103   | Elapsed: 00:01 | Remaining: 00:00
     - 47/66 : MaterialFootprint_titanium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   454 of 454   | Elapsed: 00:04 | Remaining: 00:00
     - 48/66 : MaterialFootprint_tungsten                 | [35m██████████████████████████████[0m | 100.0% | Progress:     5 of 5     | Elapsed: 00:00 | Remaining: 00:00
     - 49/66 : MaterialFootprint_uranium                  | [35m██████████████████████████████[0m | 100.0% | Progress:   136 of 136   | Elapsed: 00:01 | Remaining: 00:00
     - 50/66 : MaterialFootprint_vegetable oil            | [35m██████████████████████████████[0m | 100.0% | Progress:    34 of 34    | Elapsed: 00:00 | Remaining: 00:00
     - 51/66 : MaterialFootprint_water                    | [35m██████████████████████████████[0m | 100.0% | Progress: 10145 of 10145 | Elapsed: 02:15 | Remaining: 00:00
     - 52/66 : MaterialFootprint_zinc                     | [35m██████████████████████████████[0m | 100.0% | Progress:   557 of 557   | Elapsed: 00:09 | Remaining: 00:00
     - 53/66 : MaterialFootprint_zirconium                | [35m██████████████████████████████[0m | 100.0% | Progress:     9 of 9     | Elapsed: 00:00 | Remaining: 00:00
     - 54/66 : WasteFootprint_composting-kilogram         | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     - 55/66 : WasteFootprint_digestion-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:    16 of 16    | Elapsed: 00:00 | Remaining: 00:00
     - 56/66 : WasteFootprint_digestion-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 57/66 : WasteFootprint_hazardous-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:   423 of 423   | Elapsed: 00:06 | Remaining: 00:00
     - 58/66 : WasteFootprint_hazardous-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:  1842 of 1842  | Elapsed: 00:29 | Remaining: 00:00
     - 59/66 : WasteFootprint_incineration-cubicmeter     | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 60/66 : WasteFootprint_incineration-kilogram       | [35m██████████████████████████████[0m | 100.0% | Progress:  1897 of 1897  | Elapsed: 00:30 | Remaining: 00:00
     - 61/66 : WasteFootprint_landfill-cubicmeter         | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 62/66 : WasteFootprint_landfill-kilogram           | [35m██████████████████████████████[0m | 100.0% | Progress:  1430 of 1430  | Elapsed: 00:22 | Remaining: 00:00
     - 63/66 : WasteFootprint_openburning-kilogram        | [35m██████████████████████████████[0m | 100.0% | Progress:   535 of 535   | Elapsed: 00:08 | Remaining: 00:00
     - 64/66 : WasteFootprint_recycling-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:   129 of 129   | Elapsed: 00:02 | Remaining: 00:00
     - 65/66 : WasteFootprint_total-cubicmeter            | [35m██████████████████████████████[0m | 100.0% | Progress:  3976 of 3976  | Elapsed: 01:03 | Remaining: 00:00
     - 66/66 : WasteFootprint_total-kilogram              | [35m██████████████████████████████[0m | 100.0% | Progress: 28883 of 28883 | Elapsed: 07:45 | Remaining: 00:00


.. parsed-literal::

    ****************************************************************************************************
    
    *** ExchangeEditor() completed for ecoinvent-3.9.1-cutoff in 0:20:08 (h:m:s) ***
    
    ****************************************************************************************************
    
    ** Verifying database ecoinvent-3.9.1-cutoff in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 4.66e-11 
    	Method: Indium 
    	Activity: electricity production, photovoltaic, 3kWp slanted-roof installation, single-Si, laminated, integrated 
    	Database: ecoinvent-3.9.1-cutoff
    
    ** Database verified successfully! **
    
    ==========================================================================================
    	*** Finished T-reX for ecoinvent-3.9.1-cutoff ***
    			Duration: 0:20:27 (h:m:s)
    	*** Woah woah wee waa, great success!! ***
    ==========================================================================================
    --------------------------------------------------------------------------------
    
    
    --------------------------------------------------------------------------------
    
    ** Processing database (2/5): ecoinvent_cutoff_3.9_remind_SSP2-Base_2065**
    Arguments:
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-Base_2065', 'db_T_reX_name': 'T-reX'}
    
    
    *** ExchangeEditor() is running for ecoinvent_cutoff_3.9_remind_SSP2-Base_2065 ***
    
    * Appending T-reX exchanges in T-reX
     


.. parsed-literal::

     -  1/67 : MaterialFootprint_aluminium                | [35m██████████████████████████████[0m | 100.0% | Progress:  1925 of 1925  | Elapsed: 00:32 | Remaining: 00:00
     -  2/67 : MaterialFootprint_antimony                 | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     -  3/67 : MaterialFootprint_bauxite                  | [35m██████████████████████████████[0m | 100.0% | Progress:    24 of 24    | Elapsed: 00:00 | Remaining: 00:00
     -  4/67 : MaterialFootprint_beryllium                | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     -  5/67 : MaterialFootprint_borates                  | [35m██████████████████████████████[0m | 100.0% | Progress:    15 of 15    | Elapsed: 00:00 | Remaining: 00:00
     -  6/67 : MaterialFootprint_cadmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    17 of 17    | Elapsed: 00:00 | Remaining: 00:00
     -  7/67 : MaterialFootprint_cement                   | [35m██████████████████████████████[0m | 100.0% | Progress:  2598 of 2598  | Elapsed: 00:29 | Remaining: 00:00
     -  8/67 : MaterialFootprint_cerium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     -  9/67 : MaterialFootprint_chromium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   425 of 425   | Elapsed: 00:04 | Remaining: 00:00
     - 10/67 : MaterialFootprint_coal                     | [35m██████████████████████████████[0m | 100.0% | Progress:   146 of 146   | Elapsed: 00:01 | Remaining: 00:00
     - 11/67 : MaterialFootprint_cobalt                   | [35m██████████████████████████████[0m | 100.0% | Progress:   166 of 166   | Elapsed: 00:01 | Remaining: 00:00
     - 12/67 : MaterialFootprint_coke                     | [35m██████████████████████████████[0m | 100.0% | Progress:    71 of 71    | Elapsed: 00:00 | Remaining: 00:00
     - 13/67 : MaterialFootprint_copper                   | [35m██████████████████████████████[0m | 100.0% | Progress:  1064 of 1064  | Elapsed: 00:16 | Remaining: 00:00
     - 14/67 : MaterialFootprint_dysprosium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 15/67 : MaterialFootprint_electricity              | [35m██████████████████████████████[0m | 100.0% | Progress: 24074 of 24074 | Elapsed: 06:29 | Remaining: 00:00
     - 16/67 : MaterialFootprint_erbium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 17/67 : MaterialFootprint_europium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 18/67 : MaterialFootprint_fluorspar                | [35m██████████████████████████████[0m | 100.0% | Progress:    22 of 22    | Elapsed: 00:00 | Remaining: 00:00
     - 19/67 : MaterialFootprint_gadolinium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 20/67 : MaterialFootprint_gallium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 21/67 : MaterialFootprint_gold                     | [35m██████████████████████████████[0m | 100.0% | Progress:    10 of 10    | Elapsed: 00:00 | Remaining: 00:00
     - 22/67 : MaterialFootprint_graphite                 | [35m██████████████████████████████[0m | 100.0% | Progress:    33 of 33    | Elapsed: 00:00 | Remaining: 00:00
     - 23/67 : MaterialFootprint_helium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    46 of 46    | Elapsed: 00:00 | Remaining: 00:00
     - 24/67 : MaterialFootprint_holmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 25/67 : MaterialFootprint_hydrogen                 | [35m██████████████████████████████[0m | 100.0% | Progress:   389 of 389   | Elapsed: 00:06 | Remaining: 00:00
     - 26/67 : MaterialFootprint_indium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    13 of 13    | Elapsed: 00:00 | Remaining: 00:00
     - 27/67 : MaterialFootprint_latex                    | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 28/67 : MaterialFootprint_lithium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    52 of 52    | Elapsed: 00:00 | Remaining: 00:00
     - 29/67 : MaterialFootprint_magnesium                | [35m██████████████████████████████[0m | 100.0% | Progress:   264 of 264   | Elapsed: 00:04 | Remaining: 00:00
     - 30/67 : MaterialFootprint_natural gas              | [35m██████████████████████████████[0m | 100.0% | Progress:  5825 of 5825  | Elapsed: 01:34 | Remaining: 00:00
     - 31/67 : MaterialFootprint_nickel                   | [35m██████████████████████████████[0m | 100.0% | Progress:   369 of 369   | Elapsed: 00:05 | Remaining: 00:00
     - 32/67 : MaterialFootprint_palladium                | [35m██████████████████████████████[0m | 100.0% | Progress:    23 of 23    | Elapsed: 00:00 | Remaining: 00:00
     - 33/67 : MaterialFootprint_petroleum                | [35m██████████████████████████████[0m | 100.0% | Progress:   503 of 503   | Elapsed: 00:08 | Remaining: 00:00
     - 34/67 : MaterialFootprint_phosphate rock           | [35m██████████████████████████████[0m | 100.0% | Progress:   207 of 207   | Elapsed: 00:03 | Remaining: 00:00
     - 35/67 : MaterialFootprint_platinum                 | [35m██████████████████████████████[0m | 100.0% | Progress:   170 of 170   | Elapsed: 00:02 | Remaining: 00:00
     - 36/67 : MaterialFootprint_rare earth               | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 37/67 : MaterialFootprint_rhodium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 38/67 : MaterialFootprint_sand                     | [35m██████████████████████████████[0m | 100.0% | Progress:   560 of 560   | Elapsed: 00:08 | Remaining: 00:00
     - 39/67 : MaterialFootprint_scandium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 40/67 : MaterialFootprint_selenium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     9 of 9     | Elapsed: 00:00 | Remaining: 00:00
     - 41/67 : MaterialFootprint_silicon                  | [35m██████████████████████████████[0m | 100.0% | Progress:   364 of 364   | Elapsed: 00:05 | Remaining: 00:00
     - 42/67 : MaterialFootprint_silver                   | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 43/67 : MaterialFootprint_strontium                | [35m██████████████████████████████[0m | 100.0% | Progress:    28 of 28    | Elapsed: 00:00 | Remaining: 00:00
     - 44/67 : MaterialFootprint_tantalum                 | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     - 45/67 : MaterialFootprint_tellurium                | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 46/67 : MaterialFootprint_tin                      | [35m██████████████████████████████[0m | 100.0% | Progress:   111 of 111   | Elapsed: 00:01 | Remaining: 00:00
     - 47/67 : MaterialFootprint_titanium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   457 of 457   | Elapsed: 00:07 | Remaining: 00:00
     - 48/67 : MaterialFootprint_tungsten                 | [35m██████████████████████████████[0m | 100.0% | Progress:     5 of 5     | Elapsed: 00:00 | Remaining: 00:00
     - 49/67 : MaterialFootprint_uranium                  | [35m██████████████████████████████[0m | 100.0% | Progress:   140 of 140   | Elapsed: 00:02 | Remaining: 00:00
     - 50/67 : MaterialFootprint_vegetable oil            | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 51/67 : MaterialFootprint_water                    | [35m██████████████████████████████[0m | 100.0% | Progress: 10438 of 10438 | Elapsed: 02:48 | Remaining: 00:00
     - 52/67 : MaterialFootprint_zinc                     | [35m██████████████████████████████[0m | 100.0% | Progress:   592 of 592   | Elapsed: 00:09 | Remaining: 00:00
     - 53/67 : MaterialFootprint_zirconium                | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 54/67 : WasteFootprint_carbondioxide-kilogram      | [35m██████████████████████████████[0m | 100.0% | Progress:   119 of 119   | Elapsed: 00:01 | Remaining: 00:00
     - 55/67 : WasteFootprint_composting-kilogram         | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     - 56/67 : WasteFootprint_digestion-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:    16 of 16    | Elapsed: 00:00 | Remaining: 00:00
     - 57/67 : WasteFootprint_digestion-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 58/67 : WasteFootprint_hazardous-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:   437 of 437   | Elapsed: 00:07 | Remaining: 00:00
     - 59/67 : WasteFootprint_hazardous-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:  1928 of 1928  | Elapsed: 00:30 | Remaining: 00:00
     - 60/67 : WasteFootprint_incineration-cubicmeter     | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 61/67 : WasteFootprint_incineration-kilogram       | [35m██████████████████████████████[0m | 100.0% | Progress:  2171 of 2171  | Elapsed: 00:35 | Remaining: 00:00
     - 62/67 : WasteFootprint_landfill-cubicmeter         | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 63/67 : WasteFootprint_landfill-kilogram           | [35m██████████████████████████████[0m | 100.0% | Progress:  1530 of 1530  | Elapsed: 00:24 | Remaining: 00:00
     - 64/67 : WasteFootprint_openburning-kilogram        | [35m██████████████████████████████[0m | 100.0% | Progress:   535 of 535   | Elapsed: 00:08 | Remaining: 00:00
     - 65/67 : WasteFootprint_recycling-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:   137 of 137   | Elapsed: 00:02 | Remaining: 00:00
     - 66/67 : WasteFootprint_total-cubicmeter            | [35m██████████████████████████████[0m | 100.0% | Progress:  4360 of 4360  | Elapsed: 01:10 | Remaining: 00:00
     - 67/67 : WasteFootprint_total-kilogram              | [35m██████████████████████████████[0m | 100.0% | Progress: 29524 of 29524 | Elapsed: 07:59 | Remaining: 00:00


.. parsed-literal::

    ****************************************************************************************************
    
    *** ExchangeEditor() completed for ecoinvent_cutoff_3.9_remind_SSP2-Base_2065 in 0:24:35 (h:m:s) ***
    
    ****************************************************************************************************
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-Base_2065 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 6.89e-01 
    	Method: Silver 
    	Activity: market for oil power plant, 500MW 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2065
    
    ** Database verified successfully! **
    
    ==========================================================================================
    	*** Finished T-reX for ecoinvent_cutoff_3.9_remind_SSP2-Base_2065 ***
    			Duration: 0:24:54 (h:m:s)
    	*** Woah woah wee waa, great success!! ***
    ==========================================================================================
    --------------------------------------------------------------------------------
    
    
    --------------------------------------------------------------------------------
    
    ** Processing database (3/5): ecoinvent_cutoff_3.9_remind_SSP2-Base_2100**
    Arguments:
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-Base_2100', 'db_T_reX_name': 'T-reX'}
    
    
    *** ExchangeEditor() is running for ecoinvent_cutoff_3.9_remind_SSP2-Base_2100 ***
    
    * Appending T-reX exchanges in T-reX
     


.. parsed-literal::

     -  1/67 : MaterialFootprint_aluminium                | [35m██████████████████████████████[0m | 100.0% | Progress:  1925 of 1925  | Elapsed: 00:34 | Remaining: 00:00
     -  2/67 : MaterialFootprint_antimony                 | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     -  3/67 : MaterialFootprint_bauxite                  | [35m██████████████████████████████[0m | 100.0% | Progress:    24 of 24    | Elapsed: 00:00 | Remaining: 00:00
     -  4/67 : MaterialFootprint_beryllium                | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     -  5/67 : MaterialFootprint_borates                  | [35m██████████████████████████████[0m | 100.0% | Progress:    15 of 15    | Elapsed: 00:00 | Remaining: 00:00
     -  6/67 : MaterialFootprint_cadmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    17 of 17    | Elapsed: 00:00 | Remaining: 00:00
     -  7/67 : MaterialFootprint_cement                   | [35m██████████████████████████████[0m | 100.0% | Progress:  2598 of 2598  | Elapsed: 00:29 | Remaining: 00:00
     -  8/67 : MaterialFootprint_cerium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     -  9/67 : MaterialFootprint_chromium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   425 of 425   | Elapsed: 00:04 | Remaining: 00:00
     - 10/67 : MaterialFootprint_coal                     | [35m██████████████████████████████[0m | 100.0% | Progress:   146 of 146   | Elapsed: 00:01 | Remaining: 00:00
     - 11/67 : MaterialFootprint_cobalt                   | [35m██████████████████████████████[0m | 100.0% | Progress:   166 of 166   | Elapsed: 00:01 | Remaining: 00:00
     - 12/67 : MaterialFootprint_coke                     | [35m██████████████████████████████[0m | 100.0% | Progress:    71 of 71    | Elapsed: 00:00 | Remaining: 00:00
     - 13/67 : MaterialFootprint_copper                   | [35m██████████████████████████████[0m | 100.0% | Progress:  1064 of 1064  | Elapsed: 00:11 | Remaining: 00:00
     - 14/67 : MaterialFootprint_dysprosium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 15/67 : MaterialFootprint_electricity              | [35m██████████████████████████████[0m | 100.0% | Progress: 24074 of 24074 | Elapsed: 05:35 | Remaining: 00:00
     - 16/67 : MaterialFootprint_erbium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 17/67 : MaterialFootprint_europium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 18/67 : MaterialFootprint_fluorspar                | [35m██████████████████████████████[0m | 100.0% | Progress:    22 of 22    | Elapsed: 00:00 | Remaining: 00:00
     - 19/67 : MaterialFootprint_gadolinium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 20/67 : MaterialFootprint_gallium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 21/67 : MaterialFootprint_gold                     | [35m██████████████████████████████[0m | 100.0% | Progress:    10 of 10    | Elapsed: 00:00 | Remaining: 00:00
     - 22/67 : MaterialFootprint_graphite                 | [35m██████████████████████████████[0m | 100.0% | Progress:    33 of 33    | Elapsed: 00:00 | Remaining: 00:00
     - 23/67 : MaterialFootprint_helium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    46 of 46    | Elapsed: 00:00 | Remaining: 00:00
     - 24/67 : MaterialFootprint_holmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 25/67 : MaterialFootprint_hydrogen                 | [35m██████████████████████████████[0m | 100.0% | Progress:   389 of 389   | Elapsed: 00:06 | Remaining: 00:00
     - 26/67 : MaterialFootprint_indium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    13 of 13    | Elapsed: 00:00 | Remaining: 00:00
     - 27/67 : MaterialFootprint_latex                    | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 28/67 : MaterialFootprint_lithium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    52 of 52    | Elapsed: 00:00 | Remaining: 00:00
     - 29/67 : MaterialFootprint_magnesium                | [35m██████████████████████████████[0m | 100.0% | Progress:   264 of 264   | Elapsed: 00:04 | Remaining: 00:00
     - 30/67 : MaterialFootprint_natural gas              | [35m██████████████████████████████[0m | 100.0% | Progress:  5825 of 5825  | Elapsed: 01:33 | Remaining: 00:00
     - 31/67 : MaterialFootprint_nickel                   | [35m██████████████████████████████[0m | 100.0% | Progress:   369 of 369   | Elapsed: 00:05 | Remaining: 00:00
     - 32/67 : MaterialFootprint_palladium                | [35m██████████████████████████████[0m | 100.0% | Progress:    23 of 23    | Elapsed: 00:00 | Remaining: 00:00
     - 33/67 : MaterialFootprint_petroleum                | [35m██████████████████████████████[0m | 100.0% | Progress:   503 of 503   | Elapsed: 00:08 | Remaining: 00:00
     - 34/67 : MaterialFootprint_phosphate rock           | [35m██████████████████████████████[0m | 100.0% | Progress:   207 of 207   | Elapsed: 00:03 | Remaining: 00:00
     - 35/67 : MaterialFootprint_platinum                 | [35m██████████████████████████████[0m | 100.0% | Progress:   170 of 170   | Elapsed: 00:02 | Remaining: 00:00
     - 36/67 : MaterialFootprint_rare earth               | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 37/67 : MaterialFootprint_rhodium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 38/67 : MaterialFootprint_sand                     | [35m██████████████████████████████[0m | 100.0% | Progress:   560 of 560   | Elapsed: 00:08 | Remaining: 00:00
     - 39/67 : MaterialFootprint_scandium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 40/67 : MaterialFootprint_selenium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     9 of 9     | Elapsed: 00:00 | Remaining: 00:00
     - 41/67 : MaterialFootprint_silicon                  | [35m██████████████████████████████[0m | 100.0% | Progress:   364 of 364   | Elapsed: 00:05 | Remaining: 00:00
     - 42/67 : MaterialFootprint_silver                   | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 43/67 : MaterialFootprint_strontium                | [35m██████████████████████████████[0m | 100.0% | Progress:    28 of 28    | Elapsed: 00:00 | Remaining: 00:00
     - 44/67 : MaterialFootprint_tantalum                 | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     - 45/67 : MaterialFootprint_tellurium                | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 46/67 : MaterialFootprint_tin                      | [35m██████████████████████████████[0m | 100.0% | Progress:   111 of 111   | Elapsed: 00:01 | Remaining: 00:00
     - 47/67 : MaterialFootprint_titanium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   457 of 457   | Elapsed: 00:07 | Remaining: 00:00
     - 48/67 : MaterialFootprint_tungsten                 | [35m██████████████████████████████[0m | 100.0% | Progress:     5 of 5     | Elapsed: 00:00 | Remaining: 00:00
     - 49/67 : MaterialFootprint_uranium                  | [35m██████████████████████████████[0m | 100.0% | Progress:   140 of 140   | Elapsed: 00:02 | Remaining: 00:00
     - 50/67 : MaterialFootprint_vegetable oil            | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 51/67 : MaterialFootprint_water                    | [35m██████████████████████████████[0m | 100.0% | Progress: 10438 of 10438 | Elapsed: 02:47 | Remaining: 00:00
     - 52/67 : MaterialFootprint_zinc                     | [35m██████████████████████████████[0m | 100.0% | Progress:   592 of 592   | Elapsed: 00:09 | Remaining: 00:00
     - 53/67 : MaterialFootprint_zirconium                | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 54/67 : WasteFootprint_carbondioxide-kilogram      | [35m██████████████████████████████[0m | 100.0% | Progress:   119 of 119   | Elapsed: 00:01 | Remaining: 00:00
     - 55/67 : WasteFootprint_composting-kilogram         | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     - 56/67 : WasteFootprint_digestion-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:    16 of 16    | Elapsed: 00:00 | Remaining: 00:00
     - 57/67 : WasteFootprint_digestion-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 58/67 : WasteFootprint_hazardous-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:   437 of 437   | Elapsed: 00:07 | Remaining: 00:00
     - 59/67 : WasteFootprint_hazardous-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:  1928 of 1928  | Elapsed: 00:30 | Remaining: 00:00
     - 60/67 : WasteFootprint_incineration-cubicmeter     | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 61/67 : WasteFootprint_incineration-kilogram       | [35m██████████████████████████████[0m | 100.0% | Progress:  2171 of 2171  | Elapsed: 00:34 | Remaining: 00:00
     - 62/67 : WasteFootprint_landfill-cubicmeter         | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 63/67 : WasteFootprint_landfill-kilogram           | [35m██████████████████████████████[0m | 100.0% | Progress:  1530 of 1530  | Elapsed: 00:24 | Remaining: 00:00
     - 64/67 : WasteFootprint_openburning-kilogram        | [35m██████████████████████████████[0m | 100.0% | Progress:   535 of 535   | Elapsed: 00:08 | Remaining: 00:00
     - 65/67 : WasteFootprint_recycling-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:   137 of 137   | Elapsed: 00:02 | Remaining: 00:00
     - 66/67 : WasteFootprint_total-cubicmeter            | [35m██████████████████████████████[0m | 100.0% | Progress:  4360 of 4360  | Elapsed: 01:10 | Remaining: 00:00
     - 67/67 : WasteFootprint_total-kilogram              | [35m██████████████████████████████[0m | 100.0% | Progress: 29524 of 29524 | Elapsed: 07:56 | Remaining: 00:00


.. parsed-literal::

    ****************************************************************************************************
    
    *** ExchangeEditor() completed for ecoinvent_cutoff_3.9_remind_SSP2-Base_2100 in 0:23:34 (h:m:s) ***
    
    ****************************************************************************************************
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-Base_2100 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 5.39e-02 
    	Method: Total (kg) 
    	Activity: magnesium sulfate production 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2100
    
    ** Database verified successfully! **
    
    ==========================================================================================
    	*** Finished T-reX for ecoinvent_cutoff_3.9_remind_SSP2-Base_2100 ***
    			Duration: 0:23:53 (h:m:s)
    	*** Woah woah wee waa, great success!! ***
    ==========================================================================================
    --------------------------------------------------------------------------------
    
    
    --------------------------------------------------------------------------------
    
    ** Processing database (4/5): ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065**
    Arguments:
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065', 'db_T_reX_name': 'T-reX'}
    
    
    *** ExchangeEditor() is running for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065 ***
    
    * Appending T-reX exchanges in T-reX
     


.. parsed-literal::

     -  1/67 : MaterialFootprint_aluminium                | [35m██████████████████████████████[0m | 100.0% | Progress:  1925 of 1925  | Elapsed: 00:33 | Remaining: 00:00
     -  2/67 : MaterialFootprint_antimony                 | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     -  3/67 : MaterialFootprint_bauxite                  | [35m██████████████████████████████[0m | 100.0% | Progress:    24 of 24    | Elapsed: 00:00 | Remaining: 00:00
     -  4/67 : MaterialFootprint_beryllium                | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     -  5/67 : MaterialFootprint_borates                  | [35m██████████████████████████████[0m | 100.0% | Progress:    15 of 15    | Elapsed: 00:00 | Remaining: 00:00
     -  6/67 : MaterialFootprint_cadmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    17 of 17    | Elapsed: 00:00 | Remaining: 00:00
     -  7/67 : MaterialFootprint_cement                   | [35m██████████████████████████████[0m | 100.0% | Progress:  2598 of 2598  | Elapsed: 00:29 | Remaining: 00:00
     -  8/67 : MaterialFootprint_cerium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     -  9/67 : MaterialFootprint_chromium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   425 of 425   | Elapsed: 00:04 | Remaining: 00:00
     - 10/67 : MaterialFootprint_coal                     | [35m██████████████████████████████[0m | 100.0% | Progress:   146 of 146   | Elapsed: 00:01 | Remaining: 00:00
     - 11/67 : MaterialFootprint_cobalt                   | [35m██████████████████████████████[0m | 100.0% | Progress:   166 of 166   | Elapsed: 00:01 | Remaining: 00:00
     - 12/67 : MaterialFootprint_coke                     | [35m██████████████████████████████[0m | 100.0% | Progress:    71 of 71    | Elapsed: 00:00 | Remaining: 00:00
     - 13/67 : MaterialFootprint_copper                   | [35m██████████████████████████████[0m | 100.0% | Progress:  1064 of 1064  | Elapsed: 00:11 | Remaining: 00:00
     - 14/67 : MaterialFootprint_dysprosium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 15/67 : MaterialFootprint_electricity              | [35m██████████████████████████████[0m | 100.0% | Progress: 24074 of 24074 | Elapsed: 05:23 | Remaining: 00:00
     - 16/67 : MaterialFootprint_erbium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 17/67 : MaterialFootprint_europium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 18/67 : MaterialFootprint_fluorspar                | [35m██████████████████████████████[0m | 100.0% | Progress:    22 of 22    | Elapsed: 00:00 | Remaining: 00:00
     - 19/67 : MaterialFootprint_gadolinium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 20/67 : MaterialFootprint_gallium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 21/67 : MaterialFootprint_gold                     | [35m██████████████████████████████[0m | 100.0% | Progress:    10 of 10    | Elapsed: 00:00 | Remaining: 00:00
     - 22/67 : MaterialFootprint_graphite                 | [35m██████████████████████████████[0m | 100.0% | Progress:    33 of 33    | Elapsed: 00:00 | Remaining: 00:00
     - 23/67 : MaterialFootprint_helium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    46 of 46    | Elapsed: 00:00 | Remaining: 00:00
     - 24/67 : MaterialFootprint_holmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 25/67 : MaterialFootprint_hydrogen                 | [35m██████████████████████████████[0m | 100.0% | Progress:   389 of 389   | Elapsed: 00:06 | Remaining: 00:00
     - 26/67 : MaterialFootprint_indium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    13 of 13    | Elapsed: 00:00 | Remaining: 00:00
     - 27/67 : MaterialFootprint_latex                    | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 28/67 : MaterialFootprint_lithium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    52 of 52    | Elapsed: 00:00 | Remaining: 00:00
     - 29/67 : MaterialFootprint_magnesium                | [35m██████████████████████████████[0m | 100.0% | Progress:   264 of 264   | Elapsed: 00:04 | Remaining: 00:00
     - 30/67 : MaterialFootprint_natural gas              | [35m██████████████████████████████[0m | 100.0% | Progress:  5825 of 5825  | Elapsed: 01:33 | Remaining: 00:00
     - 31/67 : MaterialFootprint_nickel                   | [35m██████████████████████████████[0m | 100.0% | Progress:   369 of 369   | Elapsed: 00:05 | Remaining: 00:00
     - 32/67 : MaterialFootprint_palladium                | [35m██████████████████████████████[0m | 100.0% | Progress:    23 of 23    | Elapsed: 00:00 | Remaining: 00:00
     - 33/67 : MaterialFootprint_petroleum                | [35m██████████████████████████████[0m | 100.0% | Progress:   503 of 503   | Elapsed: 00:08 | Remaining: 00:00
     - 34/67 : MaterialFootprint_phosphate rock           | [35m██████████████████████████████[0m | 100.0% | Progress:   207 of 207   | Elapsed: 00:03 | Remaining: 00:00
     - 35/67 : MaterialFootprint_platinum                 | [35m██████████████████████████████[0m | 100.0% | Progress:   170 of 170   | Elapsed: 00:02 | Remaining: 00:00
     - 36/67 : MaterialFootprint_rare earth               | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 37/67 : MaterialFootprint_rhodium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 38/67 : MaterialFootprint_sand                     | [35m██████████████████████████████[0m | 100.0% | Progress:   560 of 560   | Elapsed: 00:08 | Remaining: 00:00
     - 39/67 : MaterialFootprint_scandium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 40/67 : MaterialFootprint_selenium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     9 of 9     | Elapsed: 00:00 | Remaining: 00:00
     - 41/67 : MaterialFootprint_silicon                  | [35m██████████████████████████████[0m | 100.0% | Progress:   364 of 364   | Elapsed: 00:05 | Remaining: 00:00
     - 42/67 : MaterialFootprint_silver                   | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 43/67 : MaterialFootprint_strontium                | [35m██████████████████████████████[0m | 100.0% | Progress:    28 of 28    | Elapsed: 00:00 | Remaining: 00:00
     - 44/67 : MaterialFootprint_tantalum                 | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     - 45/67 : MaterialFootprint_tellurium                | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 46/67 : MaterialFootprint_tin                      | [35m██████████████████████████████[0m | 100.0% | Progress:   111 of 111   | Elapsed: 00:01 | Remaining: 00:00
     - 47/67 : MaterialFootprint_titanium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   457 of 457   | Elapsed: 00:07 | Remaining: 00:00
     - 48/67 : MaterialFootprint_tungsten                 | [35m██████████████████████████████[0m | 100.0% | Progress:     5 of 5     | Elapsed: 00:00 | Remaining: 00:00
     - 49/67 : MaterialFootprint_uranium                  | [35m██████████████████████████████[0m | 100.0% | Progress:   140 of 140   | Elapsed: 00:02 | Remaining: 00:00
     - 50/67 : MaterialFootprint_vegetable oil            | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 51/67 : MaterialFootprint_water                    | [35m██████████████████████████████[0m | 100.0% | Progress: 10438 of 10438 | Elapsed: 02:48 | Remaining: 00:00
     - 52/67 : MaterialFootprint_zinc                     | [35m██████████████████████████████[0m | 100.0% | Progress:   592 of 592   | Elapsed: 00:09 | Remaining: 00:00
     - 53/67 : MaterialFootprint_zirconium                | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 54/67 : WasteFootprint_carbondioxide-kilogram      | [35m██████████████████████████████[0m | 100.0% | Progress:   119 of 119   | Elapsed: 00:01 | Remaining: 00:00
     - 55/67 : WasteFootprint_composting-kilogram         | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     - 56/67 : WasteFootprint_digestion-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:    16 of 16    | Elapsed: 00:00 | Remaining: 00:00
     - 57/67 : WasteFootprint_digestion-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 58/67 : WasteFootprint_hazardous-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:   437 of 437   | Elapsed: 00:07 | Remaining: 00:00
     - 59/67 : WasteFootprint_hazardous-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:  1928 of 1928  | Elapsed: 00:30 | Remaining: 00:00
     - 60/67 : WasteFootprint_incineration-cubicmeter     | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 61/67 : WasteFootprint_incineration-kilogram       | [35m██████████████████████████████[0m | 100.0% | Progress:  2171 of 2171  | Elapsed: 00:35 | Remaining: 00:00
     - 62/67 : WasteFootprint_landfill-cubicmeter         | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 63/67 : WasteFootprint_landfill-kilogram           | [35m██████████████████████████████[0m | 100.0% | Progress:  1530 of 1530  | Elapsed: 00:24 | Remaining: 00:00
     - 64/67 : WasteFootprint_openburning-kilogram        | [35m██████████████████████████████[0m | 100.0% | Progress:   535 of 535   | Elapsed: 00:08 | Remaining: 00:00
     - 65/67 : WasteFootprint_recycling-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:   137 of 137   | Elapsed: 00:02 | Remaining: 00:00
     - 66/67 : WasteFootprint_total-cubicmeter            | [35m██████████████████████████████[0m | 100.0% | Progress:  4360 of 4360  | Elapsed: 01:10 | Remaining: 00:00
     - 67/67 : WasteFootprint_total-kilogram              | [35m██████████████████████████████[0m | 100.0% | Progress: 29524 of 29524 | Elapsed: 07:57 | Remaining: 00:00


.. parsed-literal::

    ****************************************************************************************************
    
    *** ExchangeEditor() completed for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065 in 0:23:23 (h:m:s) ***
    
    ****************************************************************************************************
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 4.74e-13 
    	Method: Landfill (m3) 
    	Activity: manganese concentrate production 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065
    
    ** Database verified successfully! **
    
    ==========================================================================================
    	*** Finished T-reX for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065 ***
    			Duration: 0:23:43 (h:m:s)
    	*** Woah woah wee waa, great success!! ***
    ==========================================================================================
    --------------------------------------------------------------------------------
    
    
    --------------------------------------------------------------------------------
    
    ** Processing database (5/5): ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100**
    Arguments:
    {'project_base': 'SSP-cutoff_test', 'project_T_reX': 'T_reXootprint-SSP-cutoff_test', 'db_name': 'ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100', 'db_T_reX_name': 'T-reX'}
    
    
    *** ExchangeEditor() is running for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100 ***
    
    * Appending T-reX exchanges in T-reX
     


.. parsed-literal::

     -  1/67 : MaterialFootprint_aluminium                | [35m██████████████████████████████[0m | 100.0% | Progress:  1925 of 1925  | Elapsed: 00:30 | Remaining: 00:00
     -  2/67 : MaterialFootprint_antimony                 | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     -  3/67 : MaterialFootprint_bauxite                  | [35m██████████████████████████████[0m | 100.0% | Progress:    24 of 24    | Elapsed: 00:00 | Remaining: 00:00
     -  4/67 : MaterialFootprint_beryllium                | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     -  5/67 : MaterialFootprint_borates                  | [35m██████████████████████████████[0m | 100.0% | Progress:    15 of 15    | Elapsed: 00:00 | Remaining: 00:00
     -  6/67 : MaterialFootprint_cadmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    17 of 17    | Elapsed: 00:00 | Remaining: 00:00
     -  7/67 : MaterialFootprint_cement                   | [35m██████████████████████████████[0m | 100.0% | Progress:  2598 of 2598  | Elapsed: 00:29 | Remaining: 00:00
     -  8/67 : MaterialFootprint_cerium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     -  9/67 : MaterialFootprint_chromium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   425 of 425   | Elapsed: 00:04 | Remaining: 00:00
     - 10/67 : MaterialFootprint_coal                     | [35m██████████████████████████████[0m | 100.0% | Progress:   146 of 146   | Elapsed: 00:01 | Remaining: 00:00
     - 11/67 : MaterialFootprint_cobalt                   | [35m██████████████████████████████[0m | 100.0% | Progress:   166 of 166   | Elapsed: 00:01 | Remaining: 00:00
     - 12/67 : MaterialFootprint_coke                     | [35m██████████████████████████████[0m | 100.0% | Progress:    71 of 71    | Elapsed: 00:00 | Remaining: 00:00
     - 13/67 : MaterialFootprint_copper                   | [35m██████████████████████████████[0m | 100.0% | Progress:  1064 of 1064  | Elapsed: 00:11 | Remaining: 00:00
     - 14/67 : MaterialFootprint_dysprosium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 15/67 : MaterialFootprint_electricity              | [35m██████████████████████████████[0m | 100.0% | Progress: 24074 of 24074 | Elapsed: 05:30 | Remaining: 00:00
     - 16/67 : MaterialFootprint_erbium                   | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 17/67 : MaterialFootprint_europium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 18/67 : MaterialFootprint_fluorspar                | [35m██████████████████████████████[0m | 100.0% | Progress:    22 of 22    | Elapsed: 00:00 | Remaining: 00:00
     - 19/67 : MaterialFootprint_gadolinium               | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 20/67 : MaterialFootprint_gallium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 21/67 : MaterialFootprint_gold                     | [35m██████████████████████████████[0m | 100.0% | Progress:    10 of 10    | Elapsed: 00:00 | Remaining: 00:00
     - 22/67 : MaterialFootprint_graphite                 | [35m██████████████████████████████[0m | 100.0% | Progress:    33 of 33    | Elapsed: 00:00 | Remaining: 00:00
     - 23/67 : MaterialFootprint_helium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    46 of 46    | Elapsed: 00:00 | Remaining: 00:00
     - 24/67 : MaterialFootprint_holmium                  | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 25/67 : MaterialFootprint_hydrogen                 | [35m██████████████████████████████[0m | 100.0% | Progress:   389 of 389   | Elapsed: 00:06 | Remaining: 00:00
     - 26/67 : MaterialFootprint_indium                   | [35m██████████████████████████████[0m | 100.0% | Progress:    13 of 13    | Elapsed: 00:00 | Remaining: 00:00
     - 27/67 : MaterialFootprint_latex                    | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 28/67 : MaterialFootprint_lithium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    52 of 52    | Elapsed: 00:00 | Remaining: 00:00
     - 29/67 : MaterialFootprint_magnesium                | [35m██████████████████████████████[0m | 100.0% | Progress:   264 of 264   | Elapsed: 00:04 | Remaining: 00:00
     - 30/67 : MaterialFootprint_natural gas              | [35m██████████████████████████████[0m | 100.0% | Progress:  5825 of 5825  | Elapsed: 01:35 | Remaining: 00:00
     - 31/67 : MaterialFootprint_nickel                   | [35m██████████████████████████████[0m | 100.0% | Progress:   369 of 369   | Elapsed: 00:05 | Remaining: 00:00
     - 32/67 : MaterialFootprint_palladium                | [35m██████████████████████████████[0m | 100.0% | Progress:    23 of 23    | Elapsed: 00:00 | Remaining: 00:00
     - 33/67 : MaterialFootprint_petroleum                | [35m██████████████████████████████[0m | 100.0% | Progress:   503 of 503   | Elapsed: 00:08 | Remaining: 00:00
     - 34/67 : MaterialFootprint_phosphate rock           | [35m██████████████████████████████[0m | 100.0% | Progress:   207 of 207   | Elapsed: 00:03 | Remaining: 00:00
     - 35/67 : MaterialFootprint_platinum                 | [35m██████████████████████████████[0m | 100.0% | Progress:   170 of 170   | Elapsed: 00:02 | Remaining: 00:00
     - 36/67 : MaterialFootprint_rare earth               | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 37/67 : MaterialFootprint_rhodium                  | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 38/67 : MaterialFootprint_sand                     | [35m██████████████████████████████[0m | 100.0% | Progress:   560 of 560   | Elapsed: 00:09 | Remaining: 00:00
     - 39/67 : MaterialFootprint_scandium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     1 of 1     | Elapsed: 00:00 | Remaining: 00:00
     - 40/67 : MaterialFootprint_selenium                 | [35m██████████████████████████████[0m | 100.0% | Progress:     9 of 9     | Elapsed: 00:00 | Remaining: 00:00
     - 41/67 : MaterialFootprint_silicon                  | [35m██████████████████████████████[0m | 100.0% | Progress:   364 of 364   | Elapsed: 00:06 | Remaining: 00:00
     - 42/67 : MaterialFootprint_silver                   | [35m██████████████████████████████[0m | 100.0% | Progress:    50 of 50    | Elapsed: 00:00 | Remaining: 00:00
     - 43/67 : MaterialFootprint_strontium                | [35m██████████████████████████████[0m | 100.0% | Progress:    28 of 28    | Elapsed: 00:00 | Remaining: 00:00
     - 44/67 : MaterialFootprint_tantalum                 | [35m██████████████████████████████[0m | 100.0% | Progress:     3 of 3     | Elapsed: 00:00 | Remaining: 00:00
     - 45/67 : MaterialFootprint_tellurium                | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 46/67 : MaterialFootprint_tin                      | [35m██████████████████████████████[0m | 100.0% | Progress:   111 of 111   | Elapsed: 00:01 | Remaining: 00:00
     - 47/67 : MaterialFootprint_titanium                 | [35m██████████████████████████████[0m | 100.0% | Progress:   457 of 457   | Elapsed: 00:07 | Remaining: 00:00
     - 48/67 : MaterialFootprint_tungsten                 | [35m██████████████████████████████[0m | 100.0% | Progress:     5 of 5     | Elapsed: 00:00 | Remaining: 00:00
     - 49/67 : MaterialFootprint_uranium                  | [35m██████████████████████████████[0m | 100.0% | Progress:   140 of 140   | Elapsed: 00:02 | Remaining: 00:00
     - 50/67 : MaterialFootprint_vegetable oil            | [35m██████████████████████████████[0m | 100.0% | Progress:    37 of 37    | Elapsed: 00:00 | Remaining: 00:00
     - 51/67 : MaterialFootprint_water                    | [35m██████████████████████████████[0m | 100.0% | Progress: 10438 of 10438 | Elapsed: 02:49 | Remaining: 00:00
     - 52/67 : MaterialFootprint_zinc                     | [35m██████████████████████████████[0m | 100.0% | Progress:   592 of 592   | Elapsed: 00:09 | Remaining: 00:00
     - 53/67 : MaterialFootprint_zirconium                | [35m██████████████████████████████[0m | 100.0% | Progress:    11 of 11    | Elapsed: 00:00 | Remaining: 00:00
     - 54/67 : WasteFootprint_carbondioxide-kilogram      | [35m██████████████████████████████[0m | 100.0% | Progress:   119 of 119   | Elapsed: 00:01 | Remaining: 00:00
     - 55/67 : WasteFootprint_composting-kilogram         | [35m██████████████████████████████[0m | 100.0% | Progress:    26 of 26    | Elapsed: 00:00 | Remaining: 00:00
     - 56/67 : WasteFootprint_digestion-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:    16 of 16    | Elapsed: 00:00 | Remaining: 00:00
     - 57/67 : WasteFootprint_digestion-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:     4 of 4     | Elapsed: 00:00 | Remaining: 00:00
     - 58/67 : WasteFootprint_hazardous-cubicmeter        | [35m██████████████████████████████[0m | 100.0% | Progress:   437 of 437   | Elapsed: 00:07 | Remaining: 00:00
     - 59/67 : WasteFootprint_hazardous-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:  1928 of 1928  | Elapsed: 00:32 | Remaining: 00:00
     - 60/67 : WasteFootprint_incineration-cubicmeter     | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 61/67 : WasteFootprint_incineration-kilogram       | [35m██████████████████████████████[0m | 100.0% | Progress:  2171 of 2171  | Elapsed: 00:36 | Remaining: 00:00
     - 62/67 : WasteFootprint_landfill-cubicmeter         | [35m██████████████████████████████[0m | 100.0% | Progress:     2 of 2     | Elapsed: 00:00 | Remaining: 00:00
     - 63/67 : WasteFootprint_landfill-kilogram           | [35m██████████████████████████████[0m | 100.0% | Progress:  1530 of 1530  | Elapsed: 00:25 | Remaining: 00:00
     - 64/67 : WasteFootprint_openburning-kilogram        | [35m██████████████████████████████[0m | 100.0% | Progress:   535 of 535   | Elapsed: 00:08 | Remaining: 00:00
     - 65/67 : WasteFootprint_recycling-kilogram          | [35m██████████████████████████████[0m | 100.0% | Progress:   137 of 137   | Elapsed: 00:02 | Remaining: 00:00
     - 66/67 : WasteFootprint_total-cubicmeter            | [35m██████████████████████████████[0m | 100.0% | Progress:  4360 of 4360  | Elapsed: 01:12 | Remaining: 00:00
     - 67/67 : WasteFootprint_total-kilogram              | [35m██████████████████████████████[0m | 100.0% | Progress: 29524 of 29524 | Elapsed: 07:57 | Remaining: 00:00


.. parsed-literal::

    ****************************************************************************************************
    
    *** ExchangeEditor() completed for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100 in 0:23:38 (h:m:s) ***
    
    ****************************************************************************************************
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 6.92e-10 
    	Method: Indium 
    	Activity: market for inorganic phosphorus fertiliser, as P2O5 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100
    
    ** Database verified successfully! **
    
    ==========================================================================================
    	*** Finished T-reX for ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100 ***
    			Duration: 0:23:58 (h:m:s)
    	*** Woah woah wee waa, great success!! ***
    ==========================================================================================
    --------------------------------------------------------------------------------
    
    
    --------------------------------------------------------------------------------
    	*** Verifying all databases in the project **
    
    ** Verifying database ecoinvent-3.9.1-cutoff in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 1.81e-01 
    	Method: Cement 
    	Activity: market for sawlog and veneer log, softwood, debarked, measured as solid wood 
    	Database: ecoinvent-3.9.1-cutoff
    
    
    --------------------------------------------------------------------------------
    
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-Base_2065 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 3.20e-04 
    	Method: Indium 
    	Activity: metal coating facility construction 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2065
    
    
    --------------------------------------------------------------------------------
    
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-Base_2100 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 2.31e-06 
    	Method: Fluorspar 
    	Activity: market for tinplate scrap, sorted 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-Base_2100
    
    
    --------------------------------------------------------------------------------
    
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 0.00e+00 
    	Method: Chromium 
    	Activity: treatment of sewage sludge, 70% water, WWT, WW from hard fibreboard production, municipal incineration 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065
    
    	Score: 1.84e-04 
    	Method: Silicon 
    	Activity: chromium steel turning, primarily roughing, computer numerical controlled 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2065
    
    
    --------------------------------------------------------------------------------
    
    
    ** Verifying database ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100 in project T_reXootprint-SSP-cutoff_test **
    
    	Score: 2.82e+02 
    	Method: Electricity 
    	Activity: market for sawnwood, azobe, dried (u=15%), planed 
    	Database: ecoinvent_cutoff_3.9_remind_SSP2-PkBudg500_2100
    
    
    --------------------------------------------------------------------------------
    
    
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ================================================================================
                              T-reX Completed                       
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        Project:                  T_reXootprint-SSP-cutoff_test
        Total Databases:          5
        Successfully Processed:   5
        Duration:                 2:01:32 (h:m:s)
    
        ================================================================================
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
                                      _____________                                 
                                     /             \                                
                                   | Let's moooooo |                                
                                   | some LCA!     |                                
                                     \             /                                
                                      =============                                 
                                                  \                                 
                                                  \                                 
                                                  ^__^                              
                                              (oo)\_______                          
                                            (__)\       )\/\                        
                                                 ||----w |                          
                                                 ||     ||                          
    
    --------------------------------------------------------------------------------
    
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
    ================================================================================
    

