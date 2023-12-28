SearchMaterial
==============

The SearchMaterial module's primary function is to load data from '< db name >_exploded.pickle', execute search queries based on the list of materials, and store the results in a CSV file along with a corresponding log entry. The search queries are formatted as tuples, where the first entry is the name of the activity and the second is the material grouping, e.g. `("market for sodium borates", "borates")`. These queries are defined by the list in `queries_materials.py`, which can be easily modified by the user to change the scope or the groupings as desired.

Functionality
-------------
The module's core function, :func:`SearchMaterial`, takes a database name and a Brightway2 project as inputs. It 
searches for materials within the specified database, extracts relevant information such as ISIC and CPC 
classifications, and saves this information in CSV format. It also extracts and saves related material exchanges and saves them as separate files based on the material grouping. The files are used by the subsequent modules to edit the exchanges and to produce LCIA methods.

Search queries
--------------

The module `queries_material.py` contains the list of materials used to create demand methods in the WasteAndMaterialFootprint tool. 
The materials are chosen to match activities in the ecoinvent v3.9.1 database and future databases made with 
premise, and to align with the EU CRM list 2023. Additional strategic materials are included, along with some other 
materials of interest.

NOTE: The search function in `SearchMaterial.py` uses `str.startswith`, finding all activities that start with the material name.

.. code-block:: python

    # Filter activities based on the materials list
    acts_all = pd.DataFrame([x.as_dict() for x in db])
    materials_df = pd.DataFrame(queries_materials, columns=["name", "group"])
    
    acts = acts_all[
        acts_all["name"].apply(
            lambda x: any(x.startswith(material) for material in materials_df.name)
        )
    ].reset_index(drop=True)



The comma in material names is crucial for filtering specific activities in the database. For example, 
with the comma, the query  `market for gold,` will catch the activity `market for nickel` and `market for nickel, 90%` but not `market for nickel plating`.

.. code-block:: python

    queries_materials = [
        ("market for aluminium", "aluminium"),
        ("market for antimony", "antimony"),
        # ... [rest of the list] ...
        ("market for zirconium", "zirconium"),
    ]
    

