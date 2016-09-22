#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Sphinx configuration file for the Coconut Programming Language.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coconut.root import *  # NOQA

from recommonmark.parser import CommonMarkParser
from sphinx_bootstrap_theme import get_html_theme_path

#-----------------------------------------------------------------------------------------------------------------------
# DEFINITIONS:
#-----------------------------------------------------------------------------------------------------------------------

html_theme = "bootstrap"
html_theme_path = get_html_theme_path()

highlight_language = "coconut"

project = "Coconut"
copyright = "2015-2016, Evan Hubinger, licensed under Apache 2.0"
author = "Evan Hubinger"
version = VERSION
release = VERSION_STR_TAG

master_doc = 'README'
source_suffix = [".rst", ".md"]
source_parsers = {
    ".md": CommonMarkParser
}
