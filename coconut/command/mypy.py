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

import sys
import traceback
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from coconut.exceptions import CoconutException

try:
    from mypy.main import main
except ImportError:
    raise CoconutException("--mypy flag requires MyPy library",
                           extra="run 'pip install coconut[mypy]' to fix")

#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------


def mypy_run(args):
    """Runs mypy with given arguments and shows the result."""
    argv, sys.argv = sys.argv, [""] + args
    stdout, sys.stdout = sys.stdout, StringIO()
    stderr, sys.stderr = sys.stderr, StringIO()

    try:
        main(None)
    except:
        traceback.print_exc()

    out = []
    for line in sys.stdout.getvalue().splitlines():
        out.append((line, False))
    for line in sys.stderr.getvalue().splitlines():
        out.append((line, True))

    sys.argv, sys.stdout, sys.stderr = argv, stdout, stderr
    return out
