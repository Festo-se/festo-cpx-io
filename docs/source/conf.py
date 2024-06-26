# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys

sys.path.insert(0, os.path.abspath("../../src/"))

# -- Project information -----------------------------------------------------

project = "festo-cpx-io"
copyright = "2023, Festo SE & Co. KG"
author = "Martin Wiesner, Elias Rosch"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # Generate Sphinx documentation from python docstrings
    "sphinx.ext.napoleon",  # Support Google style docstring
    "sphinx_rtd_theme",  # Use Read-the-Docs theme
    "myst_parser",  # Use markdown files in the documentation along restructured text
]
source_suffix = [".rst", ".md"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

autoclass_content = "both"
autodoc_default_options = {
    # 'inherited-members': True,
    "members": True,  # Include members (functions, methods)
    "member-order": "bysource",
    # "special-members": True,  # Include special members (e.g., __init__)
    "undoc-members": True,  # Include members without docstrings
    # "private-members": True,  # Include private members (with leading underscore)
}
