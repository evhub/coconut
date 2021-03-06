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

from coconut.constants import (
    fixpath,
    univ_open,
    default_encoding,
    icoconut_custom_kernel_dir,
    icoconut_custom_kernel_install_loc,
    icoconut_custom_kernel_file_loc,
)

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
    if not os.path.exists(kernel_dest):
        os.makedirs(kernel_dest)
    shutil.copy(kernel_source, kernel_dest)
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


if __name__ == "__main__":
    install_custom_kernel()
