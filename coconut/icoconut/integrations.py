#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: kxmh42@github
License: Apache 2.0
Description: Endpoints for Coconut's external integrations.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import coconut.integrations

# -----------------------------------------------------------------------------------------------------------------------
# IPYTHON:
# -----------------------------------------------------------------------------------------------------------------------


def run_as_coconut(lines):
    if len(lines) == 1:
        line_str = lines[0]
        line_repr = repr(line_str)
        return [f"get_ipython().run_line_magic('coconut', {line_repr})"]
    else:
        lines_str = "\n".join(lines)
        if lines_str.startswith("# Coconut Header:"):
            return lines
        lines_repr = repr(lines_str)
        return [f"get_ipython().run_cell_magic('coconut', '', {lines_repr})"]


def load_ipython_extension(ipython):
    """Loads an extension that changes IPython into ICoconut."""
    coconut.integrations.load_ipython_extension(ipython)
    ipython.input_transformers_post.append(run_as_coconut)
