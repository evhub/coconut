#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Coconut installation requirements.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from coconut.root import *  # NOQA

import sys
import platform

import setuptools

from coconut.constants import (
    all_reqs,
    min_versions,
    version_strictly,
)

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


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


def get_reqs(which="main"):
    """Gets requirements from all_reqs with versions."""
    reqs = []
    for req in all_reqs[which]:
        req_str = req + ">=" + ver_tuple_to_str(min_versions[req])
        if req in version_strictly:
            req_str += ",<" + ver_tuple_to_str(min_versions[req][:-1]) + "." + str(min_versions[req][-1] + 1)
        reqs.append(req_str)
    return reqs


def uniqueify(reqs):
    """Make a list of requirements unique."""
    return list(set(reqs))


def unique_wrt(reqs, main_reqs):
    """Ensures reqs doesn't contain anything in main_reqs."""
    return list(set(reqs) - set(main_reqs))


def everything_in(req_dict):
    """Gets all requirements in a requirements dict."""
    return uniqueify(req for req_list in req_dict.values() for req in req_list)


#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

requirements = get_reqs()

extras = {
    "jupyter": get_reqs("jupyter"),
    "watch": get_reqs("watch"),
    "jobs": get_reqs("jobs"),
    "mypy": get_reqs("mypy"),
}

extras["ipython"] = extras["jupyter"]

extras["all"] = everything_in(extras)

extras["tests"] = uniqueify(
    get_reqs("tests")
    + (extras["jobs"] if platform.python_implementation() != "PyPy" else [])
    + (extras["jupyter"] if (PY2 and not PY26) or sys.version_info >= (3, 3) else [])
    + (extras["mypy"] if sys.version_info >= (3, 4) else [])
)

extras["docs"] = unique_wrt(get_reqs("docs"), requirements)

extras["dev"] = uniqueify(
    everything_in(extras)
    + get_reqs("dev")
)


def add_version_reqs(modern=True):
    if modern:
        global extras
        extras[":python_version<'2.7'"] = get_reqs("py26")
        extras[":python_version>='2.7'"] = get_reqs("non-py26")
        extras[":python_version<'3'"] = get_reqs("py2")
    else:
        global requirements
        if PY26:
            requirements += get_reqs("py26")
        else:
            requirements += get_reqs("non-py26")
        if PY2:
            requirements += get_reqs("py2")


if int(setuptools.__version__.split(".", 1)[0]) < 18:
    if "bdist_wheel" in sys.argv:
        raise RuntimeError("bdist_wheel not supported for setuptools versions < 18 (run 'pip install --upgrade setuptools' to fix)")
    add_version_reqs(modern=False)
else:
    add_version_reqs()

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------


def all_versions(req):
    """Get all versions of req from PyPI."""
    import requests
    url = "https://pypi.python.org/pypi/" + req + "/json"
    return tuple(requests.get(url).json()["releases"].keys())


def newer(new_ver, old_ver):
    """Determines if the first version tuple is newer than the second."""
    if old_ver == new_ver or old_ver + (0,) == new_ver:
        return False
    for n, o in zip(new_ver, old_ver):
        if not isinstance(n, int):
            o = str(o)
        if o < n:
            return True
        elif o > n:
            return False
    return None


def print_new_versions(strict=False):
    """Prints new requirement versions."""
    new_updates = []
    same_updates = []
    for req in everything_in(all_reqs):
        new_versions = []
        same_versions = []
        for ver_str in all_versions(req):
            comp = newer(ver_str_to_tuple(ver_str), min_versions[req])
            if comp is True:
                new_versions.append(ver_str)
            elif not strict and comp is None:
                same_versions.append(ver_str)
        update_str = req + ": " + ver_tuple_to_str(min_versions[req]) + " -> " + ", ".join(
            new_versions + ["(" + v + ")" for v in same_versions]
        )
        if new_versions:
            new_updates.append(update_str)
        elif same_versions:
            same_updates.append(update_str)
    print("\n".join(new_updates + same_updates))


if __name__ == "__main__":
    print_new_versions()
