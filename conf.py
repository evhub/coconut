#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Sphinx configuration file for the Coconut Programming Language.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coconut.root import *  # NOQA

from coconut.constants import (
    version_str_tag,
    without_toc,
    with_toc,
    exclude_docs_dirs,
)
from coconut.util import univ_open

import pydata_sphinx_theme  # NOQA
import myst_parser  # NOQA

# -----------------------------------------------------------------------------------------------------------------------
# README:
# -----------------------------------------------------------------------------------------------------------------------

with univ_open("README.rst", "r") as readme_file:
    readme = readme_file.read()

with univ_open("index.rst", "w") as index_file:
    index_file.write(readme.replace(without_toc, with_toc))

# -----------------------------------------------------------------------------------------------------------------------
# DEFINITIONS:
# -----------------------------------------------------------------------------------------------------------------------

from coconut.constants import (  # NOQA
    project,
    copyright,
    author,
    highlight_language,
)

version = VERSION
release = version_str_tag

html_theme = "pydata_sphinx_theme"
html_theme_options = {
}

master_doc = "index"

source_suffix = [".rst", ".md"]

exclude_patterns = list(exclude_docs_dirs)

default_role = "code"

extensions = ["myst_parser"]

myst_enable_extensions = [
    "smartquotes",
]

myst_heading_anchors = 4

html_sidebars = {
    "**": [
        "localtoc.html",
    ],
}
