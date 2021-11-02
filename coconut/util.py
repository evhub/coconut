#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Installer for the Coconut Jupyter kernel.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os
import shutil
import json
import traceback
import time
import ast
from zlib import crc32
from warnings import warn
from types import MethodType

from coconut.constants import (
    fixpath,
    default_encoding,
    icoconut_custom_kernel_dir,
    icoconut_custom_kernel_install_loc,
    icoconut_custom_kernel_file_loc,
    WINDOWS,
    reserved_prefix,
)


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def printerr(*args, **kwargs):
    """Prints to standard error."""
    print(*args, file=sys.stderr, **kwargs)


def univ_open(filename, opentype="r+", encoding=None, **kwargs):
    """Open a file using default_encoding."""
    if encoding is None:
        encoding = default_encoding
    if "b" not in opentype:
        kwargs["encoding"] = encoding
    # we use io.open from coconut.root here
    return open(filename, opentype, **kwargs)


def checksum(data):
    """Compute a checksum of the given data.
    Used for computing __coconut_hash__."""
    return crc32(data) & 0xffffffff  # necessary for cross-compatibility


def get_clock_time():
    """Get a time to use for performance metrics."""
    if PY2:
        return time.clock()
    else:
        return time.process_time()


class override(object):
    """Implementation of Coconut's @override for use within Coconut."""
    __slots__ = ("func",)

    # from _coconut_base_hashable
    def __reduce_ex__(self, _):
        return self.__reduce__()

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.__reduce__() == other.__reduce__()

    def __hash__(self):
        return hash(self.__reduce__())

    # from override
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        if PY2:
            return MethodType(self.func, obj, objtype)
        else:
            return MethodType(self.func, obj)

    def __set_name__(self, obj, name):
        if not hasattr(super(obj, obj), name):
            raise RuntimeError(obj.__name__ + "." + name + " marked with @override but not overriding anything")

    def __reduce__(self):
        return (self.__class__, (self.func,))


# -----------------------------------------------------------------------------------------------------------------------
# VERSIONING:
# -----------------------------------------------------------------------------------------------------------------------


def ver_tuple_to_str(req_ver):
    """Converts a requirement version tuple into a version string."""
    return ".".join(str(x) for x in req_ver)


def ver_str_to_tuple(ver_str):
    """Convert a version string into a version tuple."""
    out = []
    for x in ver_str.split("."):
        try:
            x = int(x)
        except ValueError:
            pass
        out.append(x)
    return tuple(out)


def get_next_version(req_ver, point_to_increment=-1):
    """Get the next version after the given version."""
    return req_ver[:point_to_increment] + (req_ver[point_to_increment] + 1,)


# -----------------------------------------------------------------------------------------------------------------------
# JUPYTER KERNEL INSTALL:
# -----------------------------------------------------------------------------------------------------------------------


def get_kernel_data_files(argv):
    """Given sys.argv, write the custom kernel file and return data_files."""
    if any(arg.startswith("bdist") for arg in argv):
        executable = "python"
    elif any(arg.startswith("install") for arg in argv):
        executable = sys.executable
    else:
        return []
    install_custom_kernel(executable)
    return [
        (
            icoconut_custom_kernel_install_loc,
            [icoconut_custom_kernel_file_loc],
        ),
    ]


def install_custom_kernel(executable=None, logger=None):
    """Force install the custom kernel."""
    kernel_source = os.path.join(icoconut_custom_kernel_dir, "kernel.json")
    kernel_dest = fixpath(os.path.join(sys.exec_prefix, icoconut_custom_kernel_install_loc))
    try:
        make_custom_kernel(executable)
        if not os.path.exists(kernel_dest):
            os.makedirs(kernel_dest)
        shutil.copy(kernel_source, kernel_dest)
    except OSError:
        existing_kernel = os.path.join(kernel_dest, "kernel.json")
        if os.path.exists(existing_kernel):
            if logger is not None:
                logger.log_exc()
            errmsg = "Failed to update Coconut Jupyter kernel installation; the 'coconut' kernel might not work properly as a result"
        else:
            if logger is None:
                traceback.print_exc()
            else:
                logger.print_exc()
            errmsg = "Coconut Jupyter kernel installation failed due to above error"
        if WINDOWS:
            errmsg += " (try again from a shell that is run as administrator)"
        else:
            errmsg += " (try again with 'sudo')"
        errmsg += "."
        if logger is None:
            warn(errmsg)
        else:
            logger.warn(errmsg)
        return None
    else:
        return kernel_dest


def make_custom_kernel(executable=None):
    """Write custom kernel file and return its directory."""
    if executable is None:
        executable = sys.executable
    kernel_dict = {
        "argv": [executable, "-m", "coconut.icoconut", "-f", "{connection_file}"],
        "display_name": "Coconut",
        "language": "coconut",
    }
    if os.path.exists(icoconut_custom_kernel_dir):
        shutil.rmtree(icoconut_custom_kernel_dir)
    os.mkdir(icoconut_custom_kernel_dir)
    with univ_open(os.path.join(icoconut_custom_kernel_dir, "kernel.json"), "wb") as kernel_file:
        raw_json = json.dumps(kernel_dict, indent=1)
        kernel_file.write(raw_json.encode(encoding=default_encoding))
    return icoconut_custom_kernel_dir


# -----------------------------------------------------------------------------------------------------------------------
# PYTEST:
# -----------------------------------------------------------------------------------------------------------------------


class FixPytestNames(ast.NodeTransformer):
    """Renames invalid names added by pytest assert rewriting."""

    def fix_name(self, name):
        """Make the given pytest name a valid but non-colliding identifier."""
        return name.replace("@", reserved_prefix + "_pytest_")

    def visit_Name(self, node):
        """Special method to visit ast.Names."""
        node.id = self.fix_name(node.id)
        return node

    def visit_alias(self, node):
        """Special method to visit ast.aliases."""
        node.asname = self.fix_name(node.asname)
        return node


def pytest_rewrite_asserts(code, module_name=reserved_prefix + "_pytest_module"):
    """Uses pytest to rewrite the assert statements in the given code."""
    from _pytest.assertion.rewrite import rewrite_asserts  # hidden since it's not always available

    module_name = module_name.encode("utf-8")
    tree = ast.parse(code)
    rewrite_asserts(tree, module_name)
    fixed_tree = ast.fix_missing_locations(FixPytestNames().visit(tree))
    return ast.unparse(fixed_tree)
