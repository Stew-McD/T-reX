FutureScenarios
===============

The `FutureScenarios` module is an integral part of the WasteAndMaterialFootprint project, enabling the creation of future scenario databases. It leverages the [premise](https://github.com/polca-project/premise) Python package to generate future scenario databases based on integrated assessment models (IAMs) for brightway2 projects.

Configuration
-------------

Before using the `FutureScenarios` module, it's crucial to set up your desired scenarios in the `user_settings.py` file. This configuration determines the specific scenarios the module will process.

Configuring Projects and Premise Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Project Settings**: Define the base and target projects for the scenarios. For instance, `project_premise_base` as the source, and `project_premise` as the destination project.
- **Database Selection**: Specify the database to use, like `ecoinvent-3.9.1-cutoff`.
- **Premise Key**: A key is required for accessing premise functionality. It can be hardcoded or read from a file.
- **Multiprocessing and Batch Size**: Decide on using multiprocessing and the size of batches to process scenarios.
- **Deletion Settings**: Choose whether to delete existing projects before creating new ones.

Selecting Scenarios
^^^^^^^^^^^^^^^^^^^

Define the models, SSPs (Shared Socioeconomic Pathways), RCPs (Representative Concentration Pathways), and years you want to explore. The script will then attempt to create databases for each combination of these parameters, provided they are available.

Implementation
--------------

Module Overview
^^^^^^^^^^^^^^^

The `FutureScenarios` module consists of several key functions and a main script that orchestrates the entire process of creating future scenario databases.

Key Functions
^^^^^^^^^^^^^

- **make_possible_scenario_list**: Generates a list of feasible scenarios based on user preferences and available data.
- **check_existing**: Checks if a scenario already exists in the project to avoid redundancy.
- **FutureScenarios**: The core function that invokes the `premise` module to create new databases for each specified scenario.
- **MakeFutureScenarios**: The main function that calls `FutureScenarios` if the `use_premise` flag is set to True.

Process Flow
^^^^^^^^^^^^

1. **Initialisation**: The script starts by importing necessary libraries and user settings. It sets up logging and changes the working directory if necessary.
2. **Scenario Filtering**: It filters out unavailable or existing scenarios.
3. **Project Preparation**: Depending on user settings, it either uses an existing project or creates a new one.
4. **Scenario Processing**: For each scenario, it calls `premise` to update or create a database reflecting that scenario.
5. **Database Writing**: After processing, the script writes the new databases to Brightway2.
6. **Cleanup and Conclusion**: The script concludes by adding GWP factors and returning to the original directory.

