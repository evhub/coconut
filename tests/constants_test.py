#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Test Coconut constants.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import unittest

from coconut import constants

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def is_hashable(obj):
    """Determine if obj is hashable."""
    try:
        hash(obj)
    except Exception:
        return False
    else:
        return True


def assert_hashable_or_dict(name, obj):
    """Assert obj is hashable, or for dicts apply recursively to values."""
    if isinstance(obj, dict):
        for val in obj.values():
            assert_hashable_or_dict(name, val)
    else:
        assert is_hashable(obj), "Constant " + name + " contains unhashable values"


#-----------------------------------------------------------------------------------------------------------------------
# TESTS:
#-----------------------------------------------------------------------------------------------------------------------


class TestConstants(unittest.TestCase):

    def test_immutable(self):
        for name, value in vars(constants).items():
            if not name.startswith("__"):
                assert not isinstance(value, list), "Constant " + name + " should be tuple, not list"
                assert not isinstance(value, set), "Constant " + name + " should be frozenset, not set"
                assert_hashable_or_dict(name, value)
