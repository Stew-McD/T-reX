# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))
sys.path.insert(0, os.path.abspath('../../config'))
sys.path.insert(0, os.path.abspath('../../data'))
sys.path.insert(0, os.path.abspath('../../examples'))

project = 'WasteAndMaterialFootprint'
copyright = '2023, Stewart Charles McDowall | Stew-McD'
author = 'Stewart Charles McDowall | Stew-McD'
release = '0.1.1'

html_theme = 'sphinx_rtd_theme'
# html_static_path = ['_static']
extensions = ['sphinx.ext.autodoc']
# templates_path = ['_templates']
exclude_patterns = []

master_doc = 'index'
latex_documents = [
    (master_doc, 'WasteAndMaterialFootprint.tex', 'WasteAndMaterialFootprint Documentation',
     'Stewart Charles McDowall', 'manual'),
]



