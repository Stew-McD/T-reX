MethodEditor
============

The MethodEditor module is a key component of the WasteAndMaterialFootprint tool, offering functionalities 
to manage methods related to waste and material footprints in a project. This module is instrumental in 
adding, deleting, and checking methods within the context of environmental impact assessments.

Function Summary
----------------
- **`AddMethods`**: This function adds new methods to a project based on entries in a custom biosphere database. 
  It is useful for incorporating specific waste and material footprint methodologies into the project's analysis framework.
- **`DeleteMethods`**: This function removes specific methods from a project, particularly those associated with 
  waste and material footprints, aiding in maintaining the relevance and accuracy of the project's methodological toolbox.
- **`CheckMethods`**: This function lists and checks the methods in a project, focusing on those linked to waste 
  and material footprints, ensuring that the methods are correctly implemented and aligned with the project's objectives.

Important Code Snippets
-----------------------
- **Function to Add Methods to a Project**:

.. code-block:: python

    def AddMethods():
        # ... snippet to show structure of method keys added ...

        # Assign characterization factor based on type
        ch_factor = -1.0 if m_type == "waste" else 1.0

        # Assign method key and description based on type
        if m_type == "waste":
            name_combined = m_code.split(" ")[0] + " combined"
            method_key = (
                "WasteAndMaterialFootprint",
                "Waste: " + name_combined,
                m_code,
            )
            description = "For estimating the waste footprint of an activity"
        else:
            method_key = ("WasteAndMaterialFootprint", "Demand: " + m_code, m_code)
            description = "For estimating the material demand footprint of an activity"

        # ... end snippet ...




- **Function to Delete Methods from a Project**:

.. code-block:: python

    def DeleteMethods():
        # Implementation of the function



- **Function to Check Methods in a Project**:

.. code-block:: python

    def CheckMethods():
        # ... snippet to show how methods are accessed ...

        methods_wasteandmaterial = [
            x for x in list(bd.methods) if "WasteAndMaterial Footprint" == x[0]
        ]

        for m in methods_wasteandmaterial:
            method = bd.Method(m)
            print(method.load())
            print(method.metadata)

        print(len(methods_wasteandmaterial))

        # ... end snippet ...





