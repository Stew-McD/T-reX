Installation
============

Dependencies
------------

The program is written in Python and the required packages are listed in the `requirements.txt` file. These should be installed automatically when installing the program.

The main dependencies are:

- `brightway2 <https://docs.brightway.dev>`_
- `premise <https://premise.readthedocs.io>`_
- `wurst <https://wurst.readthedocs.io>`_

Installation Instructions
-------------------------

**It is recommended to use a fresh virtual environment to install the program.**

You can simply clone the repo and run:

.. code-block:: bash

    python src/WasteAndMaterialFootprint/main.py

This will not install any of the dependencies, so you will need to install them manually if you don't already have them.

A better option: the program can be installed using pip:

.. code-block:: bash

    pip install WasteAndMaterialFootprint

Or, if you want to install the latest version from GitHub:

.. code-block:: bash

    pip install git+https://github.com/Stew-McD/WasteAndMaterialFootprint.git

Or for an editable install (good for development and testing):

.. code-block:: bash

    git clone https://github.com/Stew-McD/WasteAndMaterialFootprint.git
    cd WasteAndMaterialFootprint
    pip install -e .

