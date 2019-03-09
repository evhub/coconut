#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Coconut installation requirements.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from coconut.root import *  # NOQA

from coconut.constants import (
    ver_str_to_tuple,
    ver_tuple_to_str,
    all_reqs,
    min_versions,
    version_strictly,
    PYPY,
    PY34,
    IPY,
    WINDOWS,
)

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

try:
    import setuptools  # this import is expensive, so we keep it out of constants
    setuptools_version = tuple(int(x) for x in setuptools.__version__.split("."))
    using_modern_setuptools = setuptools_version >= (18,)
    supports_env_markers = setuptools_version >= (36, 2)
except Exception:
    using_modern_setuptools = False
    supports_env_markers = False

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def get_base_req(req):
    """Get the name of the required package for the given requirement."""
    if isinstance(req, tuple):
        req = req[0]
    return req.split(":", 1)[0]


def get_reqs(which="main"):
    """Gets requirements from all_reqs with versions."""
    reqs = []
    for req in all_reqs[which]:
        req_str = get_base_req(req) + ">=" + ver_tuple_to_str(min_versions[req])
        if req in version_strictly:
            req_str += ",<" + ver_tuple_to_str(min_versions[req][:-1] + (min_versions[req][-1] + 1,))
        env_marker = req[1] if isinstance(req, tuple) else None
        if env_marker:
            if env_marker == "py2":
                if supports_env_markers:
                    req_str += ";python_version<'3'"
                elif not PY2:
                    continue
            elif env_marker == "py3":
                if supports_env_markers:
                    req_str += ";python_version>='3'"
                elif PY2:
                    continue
            else:
                raise ValueError("unknown env marker id " + repr(env_marker))
        reqs.append(req_str)
    return reqs


def uniqueify(reqs):
    """Make a list of requirements unique."""
    return list(set(reqs))


def uniqueify_all(init_reqs, *other_reqs):
    """Find the union of all the given requirements."""
    union = set(init_reqs)
    for reqs in other_reqs:
        union.update(reqs)
    return list(union)


def unique_wrt(reqs, main_reqs):
    """Ensures reqs doesn't contain anything in main_reqs."""
    return list(set(reqs) - set(main_reqs))


def everything_in(req_dict):
    """Gets all requirements in a requirements dict."""
    return uniqueify(req for req_list in req_dict.values() for req in req_list)


# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------

requirements = get_reqs()

extras = {
    "jupyter": get_reqs("jupyter"),
    "watch": get_reqs("watch"),
    "jobs": get_reqs("jobs"),
    "mypy": get_reqs("mypy"),
    "asyncio": get_reqs("asyncio"),
    "cPyparsing": get_reqs("cPyparsing"),
}

extras["all"] = everything_in(extras)

extras["ipython"] = extras["jupyter"]

extras["docs"] = unique_wrt(get_reqs("docs"), requirements)

extras["tests"] = uniqueify_all(
    get_reqs("tests"),
    extras["jobs"] + get_reqs("cPyparsing") if not PYPY else [],
    extras["jupyter"] if IPY else [],
    extras["mypy"] if PY34 and not WINDOWS and not PYPY else [],
    extras["asyncio"] if not PY34 else [],
)

extras["dev"] = uniqueify_all(
    everything_in(extras),
    get_reqs("dev"),
)

if using_modern_setuptools:
    # modern method for adding version-dependent requirements
    extras[":python_version<'2.7'"] = get_reqs("py26")
    extras[":python_version>='2.7'"] = get_reqs("non-py26")
    extras[":python_version<'3'"] = get_reqs("py2")
    extras[":python_version>='3'"] = get_reqs("py3")

else:
    # old method for adding version-dependent requirements
    if PY26:
        requirements += get_reqs("py26")
    else:
        requirements += get_reqs("non-py26")
    if PY2:
        requirements += get_reqs("py2")
    else:
        requirements += get_reqs("py3")

# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------


def all_versions(req):
    """Get all versions of req from PyPI."""
    import requests
    url = "https://pypi.python.org/pypi/" + get_base_req(req) + "/json"
    return tuple(requests.get(url).json()["releases"].keys())


def newer(new_ver, old_ver, strict=False):
    """Determines if the first version tuple is newer than the second.
    True if newer, False if older, None if difference is after specified version parts."""
    if old_ver == new_ver or old_ver + (0,) == new_ver:
        return False
    for n, o in zip(new_ver, old_ver):
        if not isinstance(n, int):
            o = str(o)
        if o < n:
            return True
        elif o > n:
            return False
    return not strict


def print_new_versions(strict=False):
    """Prints new requirement versions."""
    new_updates = []
    same_updates = []
    for req in everything_in(all_reqs):
        new_versions = []
        same_versions = []
        for ver_str in all_versions(req):
            if newer(ver_str_to_tuple(ver_str), min_versions[req], strict=True):
                new_versions.append(ver_str)
            elif not strict and newer(ver_str_to_tuple(ver_str), min_versions[req]):
                same_versions.append(ver_str)
        if isinstance(req, tuple):
            base_req, env_marker = req
        else:
            base_req, env_marker = req, None
        update_str = (
            base_req + (" (" + env_marker + ")" if env_marker else "")
            + " = " + ver_tuple_to_str(min_versions[req])
            + " -> " + ", ".join(new_versions + ["(" + v + ")" for v in same_versions])
        )
        if new_versions:
            new_updates.append(update_str)
        elif same_versions:
            same_updates.append(update_str)
    print("\n".join(new_updates + same_updates))


if __name__ == "__main__":
    print_new_versions()
