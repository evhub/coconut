#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger
License: Apache 2.0
Description: Handles interfacing with MyPy to make --mypy work.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from coconut.exceptions import CoconutException

try:
    from mypy import api
except ImportError:
    raise CoconutException("--mypy flag requires MyPy library",
                           extra="run 'pip install coconut[mypy]' to fix")

#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------


def mypy_run(args):
    """Runs mypy with given arguments and shows the result."""
    stdout_results, stderr_results = api.run(args)
    for line in stdout_results.splitlines():
        yield line, False
    for line in stderr_results.splitlines():
        yield line, True
