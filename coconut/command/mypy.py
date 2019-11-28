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

import traceback

from coconut.constants import ignore_mypy_errs
from coconut.exceptions import CoconutException
from coconut.terminal import logger

try:
    from mypy.api import run
except ImportError:
    raise CoconutException(
        "--mypy flag requires MyPy library",
        extra="run 'pip install coconut[mypy]' to fix",
    )

# -----------------------------------------------------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------------------------------------------------


def mypy_run(args):
    """Runs mypy with given arguments and shows the result."""
    logger.log_cmd(["mypy"] + args)
    try:
        stdout, stderr, exit_code = run(args)
    except BaseException:
        traceback.print_exc()
    else:
        for line in stdout.splitlines():
            yield line, False
        for line in stderr.splitlines():
            for ignore_err in ignore_mypy_errs:
                if ignore_err in line:
                    continue
            yield line, True
