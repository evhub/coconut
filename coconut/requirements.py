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

from coconut.constants import all_reqs, req_vers

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def req_str(req_ver):
    """Converts a requirement version tuple into a version string."""
    return ".".join(str(x) for x in req_ver)


def get_reqs(which="main"):
    """Gets requirements from all_reqs with req_vers."""
    reqs = []
    for req in all_reqs[which]:
        cur_ver = req_str(req_vers[req])
        next_ver = req_str(req_vers[req][:-1]) + "." + str(req_vers[req][-1] + 1)
        reqs.append(req + ">=" + cur_ver + ",<" + next_ver)
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


def latest_version(req):
    """Get the latest version of req from PyPI."""
    import requests
    url = "https://pypi.python.org/pypi/" + req + "/json"
    return requests.get(url).json()["info"]["version"]


def ver_tuple(ver_str):
    """Convert a version string into a version tuple."""
    out = []
    for x in ver_str.split("."):
        try:
            x = int(x)
        except ValueError:
            pass
        out.append(x)
    return tuple(out)


def print_new_versions():
    """Prints new requirement versions."""
    for req in everything_in(all_reqs):
        new_str = latest_version(req)
        new_ver = ver_tuple(new_str)
        updated = False
        for i, x in enumerate(req_vers[req]):
            if len(new_ver) <= i or x != new_ver[i]:
                updated = True
                break
        if updated:
            print(req + ": " + req_str(req_vers[req]) + " -> " + new_str)


if __name__ == "__main__":
    print_new_versions()
