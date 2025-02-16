MakeCustomDatabase
==================

The MakeCustomDatabase module's function is to facilitate the creation and integration of custom databases into the Brightway2 project. This module is responsible for generating an xlsx representation of a Brightway2 database based on the output of the modules `SearchWaste` and `SearchMaterial` and importing it into as a database with `bwio` from the Brightway2 framework.

Main Functions
--------------
- **dbWriteExcel**: This function creates an xlsx file that represents a custom Brightway2 database, using data 
  from predefined directories and database settings.
- **dbExcel2BW**: This function imports the custom database, created by dbWriteExcel, into Brightway2, making it 
  available for the `ExchangeEditor` and `MethodEditor` modules.

Important Code Snippets
-----------------------
- **Function to Collect Filenames from Directories**:

.. code-block:: python

    def get_files_from_tree(dir_searchmaterial_results, dir_searchwaste_results):
        # Implementation of the function


- **Function to Create Excel File for Custom Database**:

.. code-block:: python

    def dbWriteExcel():
        #.... snippet to show structure of the activities in the database ... 
        for NAME in names:
        count += 1
        CODE = NAME
        UNIT = determine_unit_from_name(NAME)

        if "Waste" in NAME:
            TYPE = "waste"
            CODE = (
                NAME.replace("WasteFootprint_", "")
                .capitalize()
                .replace("kilogram", "(kg)")
                .replace("cubicmeter", "(m3)")
                .replace("-", " ")
            )
        elif "Material" in NAME:
            TYPE = "natural resource"
            CODE = NAME.replace("MaterialFootprint_", "").capitalize()
        else:
            TYPE = "?"

        db_entry = {
            "Activity": NAME,
            "categories": "water, air, land",
            "code": CODE,
            "unit": UNIT,
            "type": TYPE,
        }

    # ... ..... 


- **Function to Determine Unit from Name**:

.. code-block:: python

    def determine_unit_from_name(name):
        # Implementation of the Function


- **Function to Import Database into Brightway2**:

.. code-block:: python

    def dbExcel2BW():
        # Implementation of the Function

