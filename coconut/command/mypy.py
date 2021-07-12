#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger
License: Apache 2.0
Description: Handles interfacing with MyPy to make --mypy work.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import traceback

from coconut.exceptions import CoconutException
from coconut.terminal import logger

try:
    from mypy.api import run
except ImportError:
    raise CoconutException(
        "--mypy flag requires MyPy library",
        extra="run '{python} -m pip install coconut[mypy]' to fix".format(python=sys.executable),
    )

# -----------------------------------------------------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------------------------------------------------


def mypy_run(args):
    """Run mypy with given arguments and return the result."""
    logger.log_cmd(["mypy"] + args)
    try:
        stdout, stderr, exit_code = run(args)
    except BaseException:
        traceback.print_exc()
    else:
        for line in stdout.splitlines():
            yield line, False
        for line in stderr.splitlines():
            yield line, True
