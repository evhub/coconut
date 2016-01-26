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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "coconut"))

from root import *
from recommonmark.parser import CommonMarkParser
import sphinx_bootstrap_theme

#-----------------------------------------------------------------------------------------------------------------------
# DEFINITIONS:
#-----------------------------------------------------------------------------------------------------------------------

pygments_style = "sphinx"
html_theme = "bootstrap"
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

project = "Coconut"
copyright = "2015, Evan Hubinger"
author = "Evan Hubinger"
version = VERSION

master_doc = 'README'
htmlhelp_basename = "coconutdoc"

source_parsers = {
    ".md": CommonMarkParser
}
source_suffix = [".rst", ".md"]
