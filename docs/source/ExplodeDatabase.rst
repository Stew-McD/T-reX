ExplodeDatabase
===============

The ExplodeDatabase module is the first fundamental component of the T-reX  tool, designed for
processing Brightway2 life cycle assessment (LCA) databases. It provides a mechanism to expand a given LCA database
into a detailed list of all exchanges, facilitating subsequent analysis with the search modules.

Primary Function
-----------------

The module's core functionality is to 'explode' a Brightway2 database. This term refers to the process of decomposing
the database into a single-level, comprehensive list of all exchanges. Each exchange in the database is extracted and
documented, including detailed attributes such as name, amount, unit, product, production volume, type, and location.

Process Overview
-----------------

1. Utilising the wurst library, the module opens the specified Brightway2 database.
2. It extracts information from each process in the database.
3. The extracted data is converted into a pandas DataFrame for ease of analysis and manipulation.
4. The module then expands ('explodes') this DataFrame to detail each exchange individually.
5. The resulting data, now a comprehensive list of exchanges, is saved in a .pickle binary file for efficient storage
   and retrieval.

Usage
------

The ExplodeDatabase function is invoked with a single argument, the name of the Brightway2 database to be processed.
It performs the exploding process, logs the operation, and saves the resulting DataFrame as a pickle file. The function
is designed for internal use within the T-reX tool and does not return a value but rather saves the output for subsequent
use.
