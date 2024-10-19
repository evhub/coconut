#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Test Coconut constants.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os
import unittest

from coconut import constants
from coconut.constants import (
    WINDOWS,
    PYPY,
    PY26,
    PY39,
    fixpath,
)

if PY26:
    import_module = __import__
else:
    from importlib import import_module

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


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


def is_importable(name):
    """Determine if name can be imported."""
    try:
        import_module(name)
    except ImportError:
        return False
    else:
        return True


# -----------------------------------------------------------------------------------------------------------------------
# TESTS:
# -----------------------------------------------------------------------------------------------------------------------


class TestConstants(unittest.TestCase):

    def test_defaults(self):
        assert constants.use_fast_pyparsing_reprs
        assert constants.num_assemble_logical_lines_tries >= 1
        assert not constants.embed_on_internal_exc
        assert not constants.test_computation_graph_pickling

    def test_fixpath(self):
        assert os.path.basename(fixpath("CamelCase.py")) == "CamelCase.py"

    def test_immutable(self):
        for name, value in vars(constants).items():
            if not name.startswith("__"):
                assert not isinstance(value, list), "Constant " + name + " should be tuple, not list"
                assert not isinstance(value, set), "Constant " + name + " should be frozenset, not set"
                assert_hashable_or_dict(name, value)

    def test_imports(self):
        for new_imp, (old_imp, ver_cutoff) in constants.py3_to_py2_stdlib.items():
            if "/" in old_imp:
                new_imp, old_imp = new_imp.split(".", 1)[0], old_imp.split("./", 1)[0]
            if (
                # don't test unix-specific dbm.gnu on Windows or PyPy
                new_imp == "dbm.gnu" and (WINDOWS or PYPY)
                # don't test ttk on Python 2.6
                or PY26 and old_imp == "ttk"
                # don't test tkinter on PyPy
                or PYPY and new_imp.startswith("tkinter")
                # don't test trollius, aenum on PyPy
                or PYPY and old_imp in ("trollius", "aenum")
                # don't test typing_extensions, async_generator
                or old_imp.startswith(("typing_extensions", "async_generator"))
                # don't test _dummy_thread on Py3.9
                or PY39 and new_imp == "_dummy_thread"
            ):
                pass
            elif sys.version_info >= ver_cutoff:
                assert is_importable(new_imp), "Failed to import " + new_imp
            else:
                assert is_importable(old_imp), "Failed to import " + old_imp

    def test_reqs(self):
        assert not set(constants.unpinned_min_versions) & set(constants.pinned_min_versions), "found pinned and unpinned requirements"
        assert set(constants.max_versions) <= set(constants.pinned_min_versions) | set(("cPyparsing",)), "found unlisted constrained but unpinned requirements"
        for maxed_ver in constants.max_versions:
            assert isinstance(maxed_ver, tuple) or maxed_ver in ("pyparsing", "cPyparsing"), "maxed versions must be tagged to a specific Python version"

    def test_run_args(self):
        assert "--run" not in constants.coconut_base_run_args
        assert "--quiet" not in constants.coconut_base_run_args
        assert not any(arg.startswith("--target") for arg in constants.coconut_base_run_args)

    def test_targets(self):
        assert all(v in constants.specific_targets or v in constants.pseudo_targets for v in ROOT_HEADER_VERSIONS)

    def test_tuples(self):
        assert isinstance(constants.indchars, tuple)
        assert isinstance(constants.comment_chars, tuple)
        assert isinstance(constants.setuptools_distribution_names, tuple)


# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
