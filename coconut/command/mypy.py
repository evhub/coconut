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

from coconut.exceptions import CoconutException
from coconut.terminal import logger
from coconut.constants import (
    mypy_err_infixes,
    mypy_non_err_infixes,
    mypy_silent_err_prefixes,
    mypy_silent_non_err_prefixes,
)

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


def join_lines(lines):
    """Join connected Mypy error lines."""
    running = None
    for line in lines:
        if (
            line.startswith(mypy_silent_err_prefixes + mypy_silent_non_err_prefixes)
            or any(infix in line for infix in mypy_err_infixes + mypy_non_err_infixes)
        ):
            if running:
                yield running
            running = ""
        if running is None:
            yield line
        else:
            running += line
    if running:
        yield running


def mypy_run(args):
    """Run mypy with given arguments and return the result."""
    logger.log_cmd(["mypy"] + args)
    try:
        stdout, stderr, exit_code = run(args)
    except BaseException:
        logger.print_exc()
    else:
        for line in join_lines(stdout.splitlines(True)):
            yield line, False
        for line in join_lines(stderr.splitlines(True)):
            yield line, True
