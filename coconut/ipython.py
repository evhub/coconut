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


def add_before(condition, new_elem, elem_list):
    result = []
    for elem in elem_list:
        if condition(elem):
            result.append(new_elem)
        result.append(elem)
    return result


def run_as_coconut(lines):
    lines_str = "".join(lines)
    if lines_str.startswith("# Coconut Header:"):
        # Tracebacks in ICoconut contain a long list of irrelevant Coconut
        # import statements, e.g.:
        #     ZeroDivisionError                         Traceback (most recent call last)
        #     File <ipython-input-1-c4cb9aef220a>:10
        #           6 from coconut.__coconut__ import [... long list of import statements ...]
        #           8 # Compiled Coconut: -----------------------------------------------------------
        #     ---> 10 (print)(1 / 0)  #1: 1/0 |> print
        # Workaround: add "pass" before the "# Compiled Coconut:" line so that
        # the import line goes out of context
        return add_before(
            condition=lambda line: line.startswith("# Compiled Coconut:"),
            new_elem="pass\n",
            elem_list=lines,
        )
    return ["get_ipython().run_cell_magic('coconut', '', " + repr(lines_str) + ")"]


def load_ipython_extension(ipython):
    """Loads an extension that changes IPython into ICoconut."""
    coconut.integrations.load_ipython_extension(ipython)
    ipython.input_transformers_post.append(run_as_coconut)
