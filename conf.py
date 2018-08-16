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
)

from sphinx_bootstrap_theme import get_html_theme_path
from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify

# -----------------------------------------------------------------------------------------------------------------------
# README:
# -----------------------------------------------------------------------------------------------------------------------

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

with open("index.rst", "w") as index_file:
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

html_theme = "bootstrap"
html_theme_path = get_html_theme_path()

master_doc = "index"
exclude_patterns = ["README.*"]

source_suffix = [".rst", ".md"]
source_parsers = {
    ".md": CommonMarkParser,
}

default_role = "code"

# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------


class PatchedAutoStructify(AutoStructify, object):
    """AutoStructify by default can't handle contents directives."""

    def patched_nested_parse(self, *args, **kwargs):
        """Sets match_titles then calls stored_nested_parse."""
        kwargs["match_titles"] = True
        return self.stored_nested_parse(*args, **kwargs)

    def auto_code_block(self, *args, **kwargs):
        """Modified auto_code_block that patches nested_parse."""
        self.stored_nested_parse = self.state_machine.state.nested_parse
        self.state_machine.state.nested_parse = self.patched_nested_parse
        try:
            return super(PatchedAutoStructify, self).auto_code_block(*args, **kwargs)
        finally:
            self.state_machine.state.nested_parse = self.stored_nested_parse


def setup(app):
    app.add_config_value(
        "recommonmark_config", {
            "enable_auto_toc_tree": False,
            "enable_inline_math": False,
            "enable_auto_doc_ref": False,
        },
        True,
    )
    app.add_transform(PatchedAutoStructify)
