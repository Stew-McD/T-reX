Usage
=====

The program can be used directly from the command line, or imported as a Python module. This will run the program using the default settings. See the configuration section for more information on how to change the settings.

Command Line
------------

You should clone the repo, navigate to the ``T-reX`` folder, and then run the program using:

.. code-block:: bash

    python src/T-reX/main.py

Configuration files can be found in `src/T-reX/config/`. These can be edited before running the main script.

Python Module
-------------

The program can be imported as a Python module if it has been installed with pip. The main function can then be run using:

.. code-block:: python

    import T-reX as T-reX
    T-reX.run()

As with the command line, the configuration files can be found in `src/T-reX/config/`. These can be edited before running the main script.
It is also possible to edit the configuration settings directly in the Python script, and accessed in interactive terminal sessions like iPython and Jupyter.
For example:

.. code-block:: python

    >>> import T-reX as T-reX
    
    >>> T-reX.user_settings.use_premise
    True
    >>> T-reX.user_settings.use_T_reX
    False
    >>> T-reX.user_settings.use_T_reX = True
    >>> T-reX.user_settings.use_T_reX
    True
    >>> T-reX.user_settings.project_base
    'SSP-cutoff'
    >>> T-reX.user_settings.project_base = "other project"
    >>> T-reX.user_settings.project_base
    'other project'


The individual modules can also be imported and used separately. For example:

.. code-block:: python

    .. import T-reX as T-reX
    
    .. # only use premise
    .. T-reX.FutureScenarios.MakeFutureScenarios()

    .. # only do waste or material searches
    .. database = 'my database'
    .. project = 'my project'
    .. T-reX.ExplodeDatabase(project, database)
    .. T-reX.SearchWaste(project, database)
    .. T-reX.SearchMaterial(project, database)

    .. # check databases

    .. T-reX.VerifyDatabase(project, database)

    .. # or with the internal settings:

    .. database = T-reX.user_settings.database_name
    
    .. # check original database
    .. project_base = T-reX.user_settings.project_base
    .. T-reX.VerifyDatabase(project_base, database)
    .. # (this will return '0', because it was not edited)
    
    .. # check final database
    .. project = T-reX.user_settings.project_T_reX
    .. T-reX.VerifyDatabase(project, database)
    .. # (this will return '1', if it was edited correctly)

    

