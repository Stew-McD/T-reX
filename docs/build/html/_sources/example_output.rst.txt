
(wmf) stew@SC-McD:~/WMF-test$ python
Python 3.10.8 (main, Oct  6 2023, 11:32:51) [GCC 12.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import WasteAndMaterialFootprint as wmf
Configuration directory added to Python path: /home/stew/WMF-test/config
Using environment variable BRIGHTWAY2_DIR for data directory:
/home/stew/brightway2data
>>> wmf.run()

    ================================================================================
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                   ** Starting the WasteAndMaterialFootprint tool **                
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ================================================================================
    
Creating 2 new future databases...
	{'model': 'remind', 'pathway': 'SSP2-Base', 'year': 2030}
	{'model': 'remind', 'pathway': 'SSP2-Base', 'year': 2100}
*** Starting FutureScenarios.py ***
	Using premise version (1, 8, 1)
Deleted existing project SSP-cutoff-test
Created new project SSP-cutoff-test from default

** Using: ecoinvent-3.9.1-cutoff**


 ** Processing scenario set 1 of 2, batch size 1 **

//////////////////// EXTRACTING SOURCE DATABASE ////////////////////
Cannot find cached database. Will create one now for next time...
Getting activity data
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 21238/21238 [00:00<00:00, 200349.58it/s]
Adding exchange data to activities
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 674593/674593 [00:23<00:00, 28539.27it/s]
Filling out exchange data
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 21238/21238 [00:01<00:00, 12916.65it/s]
Set missing location of datasets to global scope.
Set missing location of production exchanges to scope of dataset.
Correct missing location of technosphere exchanges.
Correct missing flow categories for biosphere exchanges
Remove empty exchanges.
Done!

////////////////// IMPORTING DEFAULT INVENTORIES ///////////////////
Cannot find cached inventories. Will create them now for next time...
Importing default inventories...
