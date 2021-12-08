#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Compile Coconut test source.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys

from coconut.tests.main_test import comp_all

# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------


def main(args=None):
    """Compile everything with given arguments."""
    if args is None:
        args = sys.argv[1:]
    print("Compiling Coconut test suite with args %r." % args)
    comp_all(args, expect_retcode=0 if "--mypy" not in args else None, check_errors="--verbose" not in args)


if __name__ == "__main__":
    main()
