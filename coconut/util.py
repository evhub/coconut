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
from contextlib import contextmanager

if sys.version_info >= (3, 2):
    from functools import lru_cache
else:
    try:
        from backports.functools_lru_cache import lru_cache
    except ImportError:
        lru_cache = None

from coconut.constants import (
    fixpath,
    default_encoding,
    icoconut_custom_kernel_dir,
    icoconut_custom_kernel_install_loc,
    icoconut_custom_kernel_file_loc,
    WINDOWS,
    reserved_prefix,
    non_syntactic_newline,
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


first_import_time = get_clock_time()


class pickleable_obj(object):
    """Version of object that binds __reduce_ex__ to __reduce__."""

    def __reduce_ex__(self, _):
        return self.__reduce__()


class override(pickleable_obj):
    """Implementation of Coconut's @override for use within Coconut."""
    __slots__ = ("func",)

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


def clip(num, min=None, max=None):
    """Clip num to live in [min, max]."""
    return (
        min if min is not None and num < min else
        max if max is not None and num > max else
        num
    )


def logical_lines(text, keep_newlines=False):
    """Iterate over the logical code lines in text."""
    prev_content = None
    for line in text.splitlines(True):
        real_line = True
        if line.endswith("\r\n"):
            if not keep_newlines:
                line = line[:-2]
        elif line.endswith(("\n", "\r")):
            if not keep_newlines:
                line = line[:-1]
        else:
            if prev_content is None:
                prev_content = ""
            prev_content += line
            real_line = False
        if real_line:
            if prev_content is not None:
                line = prev_content + line
                prev_content = None
            yield line
    if prev_content is not None:
        yield prev_content


def normalize_newlines(text):
    """Normalize all newlines in text to \\n."""
    norm_text = text.replace(non_syntactic_newline, "\n").replace("\r", "\n")
    assert len(norm_text) == len(text), "failed to normalize newlines"
    return norm_text


def get_encoding(fileobj):
    """Get encoding of a file."""
    # sometimes fileobj.encoding is undefined, but sometimes it is None; we need to handle both cases
    obj_encoding = getattr(fileobj, "encoding", None)
    return obj_encoding if obj_encoding is not None else default_encoding


def clean(inputline, rstrip=True, encoding_errors="replace"):
    """Clean and strip trailing newlines."""
    stdout_encoding = get_encoding(sys.stdout)
    inputline = str(inputline)
    if rstrip:
        inputline = inputline.rstrip("\n\r")
    return inputline.encode(stdout_encoding, encoding_errors).decode(stdout_encoding)


def displayable(inputstr, strip=True):
    """Make a string displayable with minimal loss of information."""
    out = clean(str(inputstr), False, encoding_errors="backslashreplace")
    if strip:
        out = out.strip()
    return out


def get_name(expr):
    """Get the name of an expression for displaying."""
    name = expr if isinstance(expr, str) else None
    if name is None:
        name = getattr(expr, "name", None)
    if name is None:
        name = displayable(expr)
    return name


@contextmanager
def noop_ctx():
    """A context manager that does nothing."""
    yield


def memoize(maxsize=None, *args, **kwargs):
    """Decorator that memoizes a function, preventing it from being recomputed
    if it is called multiple times with the same arguments."""
    if lru_cache is None:
        return lambda func: func
    else:
        return lru_cache(maxsize, *args, **kwargs)


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


def get_target_info(target):
    """Return target information as a version tuple."""
    if not target:
        return ()
    elif len(target) == 1:
        return (int(target),)
    else:
        return (int(target[0]), int(target[1:]))


def get_displayable_target(target):
    """Get a displayable version of the target."""
    try:
        return ver_tuple_to_str(get_target_info(target))
    except ValueError:
        return target


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
