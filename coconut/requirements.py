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

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

all_reqs = {
    "main": [
        "pyparsing",
    ],
    "dev": [
        "pre-commit",
        "requests",
    ],
    "docs": [
        "sphinx",
        "pygments",
        "recommonmark",
        "sphinx_bootstrap_theme",
    ],
    "jobs": [
        "psutil",
    ],
    "jupyter": [
        "jupyter",
        "jupyter-console",
        "ipython",
    ],
    "mypy": [
        "mypy-lang",
    ],
    "non-py26": [
        "pygments",
        "prompt_toolkit",
    ],
    "py2": [
        "futures",
    ],
    "py26": [
        "argparse",
    ],
    "tests": [
        "pytest",
    ],
    "typed-ast": [
        "typed_ast",
    ],
    "watch": [
        "watchdog",
    ],
}

versions = {
    "pyparsing": (2, 1, 10),
    "pre-commit": (0, 11, 0),
    "sphinx": (1, 4, 6),
    "pygments": (2, 1, 3),
    "recommonmark": (0, 4, 0),
    "sphinx_bootstrap_theme": (0, 4, 13),
    "psutil": (5, 0, 1),
    "jupyter": (1, 0, 0),
    "jupyter-console": (4, 1, 1),
    "ipython": (4, 2, 1),
    "mypy-lang": (0, 4, 6),
    "prompt_toolkit": (1, 0, 9),
    "futures": (3, 0, 5),
    "argparse": (1, 4, 0),
    "pytest": (3, 0, 5),
    "typed_ast": (0, 6, 3),
    "watchdog": (0, 8, 3),
    "requests": (2, 12, 5),
}

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def read_reqs(which="main"):
    """Gets requirements from all_reqs with versions."""
    reqs = []
    for req in all_reqs[which]:
        cur_ver = ".".join(str(x) for x in versions[req])
        next_ver = str(versions[req][0]) + "." + str(versions[req][1] + 1)
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
# RESOURCES:
#-----------------------------------------------------------------------------------------------------------------------

requirements = read_reqs()

if PY26:
    requirements += read_reqs("py26")
else:
    requirements += read_reqs("non-py26")

if PY2:
    requirements += read_reqs("py2")

extras = {
    "jupyter": read_reqs("jupyter"),
    "watch": read_reqs("watch"),
    "jobs": read_reqs("jobs"),
    "mypy": read_reqs("mypy"),
}

if sys.version_info >= (3, 3) and platform.system() != "Windows":
    extras["mypy"] += read_reqs("typed-ast")

extras["ipython"] = extras["jupyter"]

extras["all"] = everything_in(extras)

extras["tests"] = uniqueify(
    read_reqs("tests")
    + (extras["jobs"] if platform.python_implementation() != "PyPy" else [])
    + (extras["jupyter"] if (PY2 and not PY26) or sys.version_info >= (3, 3) else [])
    + (extras["mypy"] if not PY2 else [])
)

extras["docs"] = unique_wrt(read_reqs("docs"), requirements)

extras["dev"] = uniqueify(
    everything_in(extras)
    + read_reqs("dev")
)

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------


def latest_version(req):
    """Get the latest version of req from PyPI."""
    import requests
    url = "https://pypi.python.org/pypi/" + req + "/json"
    return requests.get(url).json()["info"]["version"]


def print_new_versions():
    """Prints new versions."""
    reqs = set()
    for name in all_reqs:
        for req in all_reqs[name]:
            reqs.add(req)
    for req in reqs:
        old = ".".join(str(x) for x in versions[req])
        new = latest_version(req)
        if old != new:
            print(req + ": " + old + " -> " + new)


if __name__ == "__main__":
    print_new_versions()
