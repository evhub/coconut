#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Adam Forest, Claude
License: Apache 2.0
Description: Opt-in pytest plugin for collecting and running Coconut test files.

Enable it with `pytest -p coconut.pytest_plugin`, or by adding
`pytest_plugins = ["coconut.pytest_plugin"]` to your top-level conftest.py.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import sys
import fnmatch
from contextlib import contextmanager

import pytest

from coconut.constants import (
    code_exts,
    coconut_cache_dir,
)
from coconut.api import (
    CoconutImporter,
    coconut_importer,
    auto_compilation,
)

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTER:
# -----------------------------------------------------------------------------------------------------------------------


class InPlaceCoconutImporter(CoconutImporter, object):
    """CoconutImporter that compiles in-place and loads the in-place compiled file.

    pytest requires that the __file__ of each imported test module match the
    path that it collected, so Coconut test files (and any Coconut modules they
    import) need to be compiled in-place rather than into __coconut_cache__,
    and loaded from there rather than letting other importers pick them up."""

    def __init__(self, *args):
        super(InPlaceCoconutImporter, self).__init__(*(("--no-cache",) + args))

    def find_spec(self, fullname, path=None, target=None):
        """Get a modulespec for the in-place compiled version of a Coconut module."""
        destpath = self.find_coconut(fullname, path)
        if destpath is None:
            return None
        from importlib.util import spec_from_file_location
        if os.path.isdir(destpath):
            return spec_from_file_location(
                fullname,
                os.path.join(destpath, "__init__.py"),
                submodule_search_locations=[destpath],
            )
        return spec_from_file_location(fullname, destpath)


in_place_importer = InPlaceCoconutImporter()


# -----------------------------------------------------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------------------------------------------------


def pytest_configure(config):
    """Compile Coconut modules imported during the test session in-place."""
    # the in-place importer takes over for the normal Coconut import hook during the test session
    config._coconut_auto_compilation_was_on = coconut_importer in sys.meta_path
    auto_compilation(False)
    if in_place_importer not in sys.meta_path:
        # go after pytest's assertion rewriting import hook (so that it can still
        #  rewrite the compiled test modules) but before everything else
        insert_ind = 0
        for i, finder in enumerate(sys.meta_path):
            if type(finder).__name__ == "AssertionRewritingHook":
                insert_ind = i + 1
                break
        sys.meta_path.insert(insert_ind, in_place_importer)


def pytest_unconfigure(config):
    """Remove the in-place Coconut importer and restore the normal Coconut import hook."""
    try:
        sys.meta_path.remove(in_place_importer)
    except ValueError:
        pass
    if getattr(config, "_coconut_auto_compilation_was_on", False):
        auto_compilation(True)


def is_coconut_test_file(file_path, config):
    """Determine whether the given path is a Coconut test file according to pytest's python_files option."""
    if file_path.suffix not in code_exts:
        return False
    for pattern in config.getini("python_files"):
        base_pattern, ext = os.path.splitext(pattern)
        if ext == ".py" and fnmatch.fnmatch(file_path.stem, base_pattern):
            return True
    return False


@contextmanager
def capturing_stderr():
    """Capture anything written to sys.stderr."""
    from io import StringIO
    captured = StringIO()
    old_stderr, sys.stderr = sys.stderr, captured
    try:
        yield captured
    finally:
        sys.stderr = old_stderr


class CoconutTestFile(pytest.File):
    """A Coconut test file, which collects the in-place compiled Python module."""

    def collect(self):
        with capturing_stderr() as compile_errors:
            try:
                compiled_path = in_place_importer.compile(str(self.path), package=False)
            except SystemExit:
                compiled_path = None
        if compiled_path is None:
            raise self.CollectError("failed to compile Coconut test file:\n" + compile_errors.getvalue())
        yield pytest.Module.from_parent(self, path=type(self.path)(compiled_path))


def pytest_collect_file(file_path, parent):
    """Collect Coconut test files."""
    if is_coconut_test_file(file_path, parent.config):
        return CoconutTestFile.from_parent(parent, path=file_path)
    return None


def pytest_ignore_collect(collection_path, config):
    """Don't separately collect compiled Python files for Coconut sources or Coconut cache directories."""
    if collection_path.name == coconut_cache_dir:
        return True
    if collection_path.suffix == ".py":
        for ext in code_exts:
            if collection_path.with_suffix(ext).exists():
                return True
    return None
