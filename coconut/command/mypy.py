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

import traceback

from coconut.exceptions import CoconutException

try:
    from mypy.api import run
except ImportError:
    raise CoconutException("--mypy flag requires MyPy library",
                           extra="run 'pip install coconut[mypy]' to fix")

#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------


def mypy_run(args):
    """Runs mypy with given arguments and shows the result."""
    try:
        stdout, stderr, exit_code = run(args)
    except BaseException:
        return traceback.format_exc()
    lines = []
    for line in stdout.splitlines():
        lines.append(line)
    for line in stderr.splitlines():
        lines.append(line)
    return "\n".join(lines)
