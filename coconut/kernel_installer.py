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

from coconut.constants import icoconut_custom_kernel_dir, icoconut_custom_kernel_install_loc

# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------


def get_kernel_data_files(argv):
    """Given sys.argv, write the custom kernel file and return data_files."""
    if any(arg.startswith("bdist") for arg in argv):
        executable = "python"
    elif any(arg.startswith("install") for arg in argv):
        executable = sys.executable
    else:
        return []
    kernel_file = make_custom_kernel(executable)
    return [
        (
            icoconut_custom_kernel_install_loc,
            [kernel_file],
        ),
    ]


def make_custom_kernel(executable=None):
    """Write custom kernel file and return its path."""
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
    dest_path = os.path.join(icoconut_custom_kernel_dir, "kernel.json")
    with open(dest_path, "w") as kernel_file:
        json.dump(kernel_dict, kernel_file, indent=1)
    return dest_path


def make_custom_kernel_and_get_dir(executable=None):
    """Write custom kernel file and return its directory."""
    make_custom_kernel(executable)
    return icoconut_custom_kernel_dir
