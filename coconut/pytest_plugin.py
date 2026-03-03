#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Adam Forest
License: Apache 2.0
Description: Pytest plugin for automatic Coconut compilation.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import io

from coconut.constants import code_exts, coconut_cache_dir

# -----------------------------------------------------------------------------------------------------------------------
# HELPERS:
# -----------------------------------------------------------------------------------------------------------------------


class _TtyStdin(io.StringIO):
    """Fake stdin that reports itself as a TTY.

    Under pytest, stdin is captured and raises OSError on read().
    Coconut's stdin_readable() checks isatty() to decide whether to read;
    returning True here makes it skip the read entirely.
    """
    def isatty(self):
        return True


_pytest_importer = None


def _get_pytest_importer():
    """Get or create the stdin-safe CoconutImporter for use under pytest."""
    global _pytest_importer
    if _pytest_importer is None:
        from coconut.api import CoconutImporter

        class _PytestCoconutImporter(CoconutImporter):
            """CoconutImporter for use under pytest.

            Compiles in-place (--no-cache) so that the path returned by
            pytest_collect_file matches what Python's import system loads,
            avoiding __file__ mismatch errors.

            Overrides find_spec to return a concrete spec pointing to the
            in-place .py file, preventing the global coconut_importer (which
            uses a cache dir) from intercepting imports and redirecting to a
            different path.

            Guards sys.stdin during every compile() call so pytest's stdin
            capture does not cause OSError.
            """

            def compile(self, path, package):
                old_stdin = sys.stdin
                sys.stdin = _TtyStdin()
                try:
                    return super(_PytestCoconutImporter, self).compile(path, package)
                finally:
                    sys.stdin = old_stdin

            def find_spec(self, fullname, path=None, target=None):
                destpath = self.find_coconut(fullname, path)
                if destpath is None:
                    return None
                from importlib.machinery import SourceFileLoader
                from importlib.util import spec_from_loader
                return spec_from_loader(fullname, SourceFileLoader(fullname, destpath))

        # --no-cache: compile in-place next to the .coco file so the
        # collected .py path and module.__file__ always agree.
        _pytest_importer = _PytestCoconutImporter("--no-cache")
    return _pytest_importer


# -----------------------------------------------------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------------------------------------------------


def pytest_configure(config):
    """Register the pytest-safe Coconut importer for the test session."""
    importer = _get_pytest_importer()
    if importer not in sys.meta_path:
        sys.meta_path.insert(0, importer)


def pytest_collect_file(file_path, parent):
    """Compile .coco test files and collect the resulting in-place .py file."""
    if file_path.suffix in code_exts and file_path.stem.startswith("test_"):
        from pathlib import Path
        import pytest
        importer = _get_pytest_importer()
        py_path = Path(importer.compile(str(file_path), package=False))
        return pytest.Module.from_parent(parent, path=py_path)


def pytest_ignore_collect(collection_path, config):
    """Skip cache directories and .py files that have a .coco source alongside them."""
    # Ignore the entire __coconut_cache__ directory tree
    if coconut_cache_dir in collection_path.parts:
        return True
    # Ignore .py files whose .coco source will be compiled and collected separately
    if collection_path.suffix == ".py" and collection_path.stem.startswith("test_"):
        for ext in code_exts:
            coco_sibling = collection_path.with_suffix(ext)
            if coco_sibling.exists():
                return True
