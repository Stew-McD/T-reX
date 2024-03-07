VerifyDatabase
==============

The VerifyDatabase module contains functionality for verifying an edited T-reX database within a given project in Brightway2. It performs this verification by calculating LCA scores for random activities within the specified database using selected methods.

Function Summary
----------------

- **`VerifyDatabase`**: This function verifies a database within a Brightway2 project by calculating LCA scores 
  for random activities using Waste Footprint and Material Demand Footprint methods. Since it is not expected that every activity and method combination would result in a non-zero score, the function allows users to specify the number of activities and methods to be used in the verification process. The function also allows users to specify whether they want to check the Waste Footprint, Material Demand Footprint, or both. 

  .. code-block:: python

    def VerifyDatabase(project_name, database_name, check_material=True, check_waste=True, log=True):
        # ... snippet to show verification process ... #

        print(f"\n** Verifying database {database_name} in project {project_name} **\n")

        # Loop until a non-zero score is obtained
        while lca_score == 0 and count < 5:
            try:
                count += 1
                # Get a random activity from the database
                act = bd.Database(database_name).random()

                # Initialize the list of methods
                methods = []

                # Find methods related to Waste Footprint
                if check_waste:
                    methods_waste = [x for x in bd.methods if "Waste" in x[1]]
                    methods += methods_waste

                # Find methods related to Material Demand Footprint
                if check_material:
                    methods_material = [x for x in bd.methods if "Demand" in x[1]]
                    methods += methods_material

                if not check_waste and not check_material:
                    method = bd.methods.random()
                    methods.append(method)

                # Choose a random method
                method = choice(methods)

                # Perform LCA calculation
                lca = bc.LCA({act: 1}, method)
                lca.lci()
                lca.lcia()

                # Get the lca score
                lca_score = lca.score

                # Print the result
                log_statement = f"\tScore: {lca_score:2.2e} \n\tMethod: {method[2]} \n\tActivity: {act['name']} \n\tDatabase: {database_name}\n"

            except Exception as e:
                # Print any errors that occur
                log_statement = (
                    f"@@@@@@@@  Error occurred with '{database_name}': {e}! @@@@@@@@"
                )

        # ...  end snippet ... #

Usage
-----

This function is called automatically after each database is processed, and again after all databases have been processed. The function can also be called manually by the user by invoking the following command:

.. code-block:: python

    T-reX.VerifyDatabase(project_name, database_name, check_material=True, check_waste=True, log=True)

    

