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
from zlib import crc32
from warnings import warn

from coconut.constants import (
    fixpath,
    default_encoding,
    icoconut_custom_kernel_dir,
    icoconut_custom_kernel_install_loc,
    icoconut_custom_kernel_file_loc,
    WINDOWS,
)


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def printerr(*args):
    """Prints to standard error."""
    print(*args, file=sys.stderr)


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


def install_custom_kernel(executable=None):
    """Force install the custom kernel."""
    make_custom_kernel(executable)
    kernel_source = os.path.join(icoconut_custom_kernel_dir, "kernel.json")
    kernel_dest = fixpath(os.path.join(sys.exec_prefix, icoconut_custom_kernel_install_loc))
    try:
        if not os.path.exists(kernel_dest):
            os.makedirs(kernel_dest)
        shutil.copy(kernel_source, kernel_dest)
    except OSError:
        existing_kernel = os.path.join(kernel_dest, "kernel.json")
        if os.path.exists(existing_kernel):
            errmsg = "Failed to update Coconut Jupyter kernel installation; the 'coconut' kernel might not work properly as a result"
        else:
            traceback.print_exc()
            errmsg = "Coconut Jupyter kernel installation failed due to above error"
        if WINDOWS:
            errmsg += " (try again from a shell that is run as administrator)"
        else:
            errmsg += " (try again with 'sudo')"
        errmsg += "."
        warn(errmsg)
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
