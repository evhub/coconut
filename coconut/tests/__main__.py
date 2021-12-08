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
    # process args
    if args is None:
        args = sys.argv[1:]
    try:
        target_ind = args.index("--target")
    except ValueError:
        agnostic_target = None
    else:
        agnostic_target = args[target_ind + 1]
        args = args[:target_ind] + args[target_ind + 2:]

    # compile everything
    print("Compiling Coconut test suite with args %r and agnostic_target=%r." % (args, agnostic_target))
    comp_all(
        args,
        agnostic_target=agnostic_target,
        expect_retcode=0 if "--mypy" not in args else None,
        check_errors="--verbose" not in args,
    )


if __name__ == "__main__":
    main()
