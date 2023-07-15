#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: kxmh42@github
License: Apache 2.0
Description: Endpoint for Coconut's integration with IPython.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import coconut.integrations

# -----------------------------------------------------------------------------------------------------------------------
# IPYTHON:
# -----------------------------------------------------------------------------------------------------------------------

__all__ = ["load_ipython_extension"]


def run_as_coconut(lines):
    lines_str = "".join(lines)
    if lines_str.startswith("# Coconut Header:"):
        return lines
    lines_repr = repr(lines_str)
    return [f"get_ipython().run_cell_magic('coconut', '', {lines_repr})"]


def load_ipython_extension(ipython):
    """Loads an extension that changes IPython into ICoconut."""
    coconut.integrations.load_ipython_extension(ipython)
    ipython.input_transformers_post.append(run_as_coconut)
