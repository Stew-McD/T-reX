# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import os
import sys
sys.path.insert(0, os.path.abspath('../src/WasteAndMaterialFootprint'))
sys.path.insert(0, os.path.abspath('../config'))
sys.path.insert(0, os.path.abspath('../data'))
sys.path.insert(0, os.path.abspath('../examples'))

project = 'WasteAndMaterialFootprint'
author = 'Stewart Charles McDowall'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_static_path = ['_static']

# Define substitutions for header lines
# rst_prolog = """
# .. |equals_line| replace:: ===============================================================
# .. |license_line| replace:: License: The Unlicense
# """
