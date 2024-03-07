# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Set an environment variable to indicate that we're running a Sphinx build
# os.environ["SPHINX_BUILD"] = "1"

sys.path.insert(0, os.path.abspath("../../src/T-reX/"))
sys.path.insert(0, os.path.abspath("../../src/T-reX/config"))
# sys.path.insert(0, os.path.abspath("../../data"))
# sys.path.insert(0, os.path.abspath("../../examples"))

project = "T-reX"
copyright = "2024, Stewart Charles McDowall | Stew-McD"
author = "Stewart Charles McDowall | Stew-McD"
release = "0.2.0"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = []

extensions = [
    "autoapi.extension",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
]
autoapi_dirs = [
    "../../src/T-reX/",
]

autosectionlabel_prefix_document = True
autosummary_generate = True

master_doc = "index"
latex_documents = [
    (
        master_doc,
        "T-reX.tex",
        "T-reX Documentation",
        "Stewart Charles McDowall",
        "manual",
    ),
]
