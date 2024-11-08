Installation
============

Dependencies
------------

The program is written in Python and the required packages are listed in the `requirements.txt` file. These should be installed automatically when installing the program.

The main dependencies are:

- `brightway2 components: bw2io, bw2data, bw2calc <https://docs.brightway.dev>`_
- `premise <https://premise.readthedocs.io>`_
- `wurst <https://wurst.readthedocs.io>`_

Installation Instructions
-------------------------

**It is recommended to use a fresh virtual environment to install the program.**

You can simply clone or download the repo and run it without installation:

.. code-block:: bash

    python venv -m <name>
    source <name>/bin/activate

This will not install any of the dependencies, so you will need to install them manually if you don't already have them.

.. code-block:: bash

    pip install -r requirements.txt


Alternatively: the program can be installed using pip:

Either from PyPI:

.. code-block:: bash

    pip install T_reX_LCA

Or, probably best to install the latest version from GitHub:

.. code-block:: bash

    pip install git+https://github.com/Stew-McD/T-reX.git

Or for an editable install (good for development and testing):

.. code-block:: bash

    git clone https://github.com/Stew-McD/T-reX.git
    cd T-reX
    pip install -e .

