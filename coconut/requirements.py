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

import sys
import time
import traceback

from coconut import embed
from coconut.constants import (
    PYPY,
    CPYTHON,
    PY34,
    IPY,
    WINDOWS,
    PURE_PYTHON,
    all_reqs,
    min_versions,
    max_versions,
    pinned_reqs,
    requests_sleep_times,
    embed_on_internal_exc,
)
from coconut.util import (
    ver_str_to_tuple,
    ver_tuple_to_str,
    get_next_version,
)

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

try:
    import setuptools  # this import is expensive, so we keep it out of constants
    setuptools_version = tuple(int(x) for x in setuptools.__version__.split(".")[:2])
    using_modern_setuptools = setuptools_version >= (18,)
    supports_env_markers = setuptools_version >= (36, 2)
except Exception:
    using_modern_setuptools = False
    supports_env_markers = False

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def get_base_req(req, include_extras=True):
    """Get the name of the required package for the given requirement."""
    if isinstance(req, tuple):
        req = req[0]
    if not include_extras:
        req = req.split("[", 1)[0]
    return req


def get_reqs(which):
    """Gets requirements from all_reqs with versions."""
    reqs = []
    for req in all_reqs[which]:
        use_req = True
        req_str = get_base_req(req) + ">=" + ver_tuple_to_str(min_versions[req])
        if req in max_versions:
            max_ver = max_versions[req]
            if max_ver is None:
                max_ver = get_next_version(min_versions[req])
            if None in max_ver:
                assert all(v is None for v in max_ver), "invalid max version " + repr(max_ver)
                max_ver = get_next_version(min_versions[req], len(max_ver) - 1)
            req_str += ",<" + ver_tuple_to_str(max_ver)
        env_marker = req[1] if isinstance(req, tuple) else None
        if env_marker:
            markers = []
            for mark in env_marker.split(";"):
                if mark.startswith("py") and mark.endswith("-only"):
                    ver = mark[len("py"):-len("-only")]
                    if len(ver) == 1:
                        ver_tuple = (int(ver),)
                    else:
                        ver_tuple = (int(ver[0]), int(ver[1:]))
                    next_ver_tuple = get_next_version(ver_tuple)
                    if supports_env_markers:
                        markers.append("python_version>='" + ver_tuple_to_str(ver_tuple) + "'")
                        markers.append("python_version<'" + ver_tuple_to_str(next_ver_tuple) + "'")
                    elif sys.version_info < ver_tuple or sys.version_info >= next_ver_tuple:
                        use_req = False
                        break
                elif mark == "py2":
                    if supports_env_markers:
                        markers.append("python_version<'3'")
                    elif not PY2:
                        use_req = False
                        break
                elif mark == "py3":
                    if supports_env_markers:
                        markers.append("python_version>='3'")
                    elif PY2:
                        use_req = False
                        break
                elif mark.startswith("py3"):
                    ver = mark[len("py3"):]
                    if supports_env_markers:
                        markers.append("python_version>='3.{ver}'".format(ver=ver))
                    elif sys.version_info < (3, ver):
                        use_req = False
                        break
                elif mark == "cpy":
                    if supports_env_markers:
                        markers.append("platform_python_implementation=='CPython'")
                    elif not CPYTHON:
                        use_req = False
                        break
                elif mark.startswith("mark"):
                    pass  # ignore
                else:
                    raise ValueError("unknown env marker " + repr(mark))
            if markers:
                req_str += ";" + " and ".join(markers)
        if use_req:
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

requirements = get_reqs("main")

extras = {
    "jupyter": get_reqs("jupyter"),
    "watch": get_reqs("watch"),
    "jobs": get_reqs("jobs"),
    "mypy": get_reqs("mypy"),
    "asyncio": get_reqs("asyncio"),
}

extras["all"] = everything_in(extras)

extras.update({
    "ipython": extras["jupyter"],
    "docs": unique_wrt(get_reqs("docs"), requirements),
    "tests": uniqueify_all(
        get_reqs("tests"),
        get_reqs("purepython"),
        extras["jobs"] if not PYPY else [],
        extras["jupyter"] if IPY else [],
        extras["mypy"] if PY34 and not WINDOWS and not PYPY else [],
        extras["asyncio"] if not PY34 and not PYPY else [],
    ),
})

extras["dev"] = uniqueify_all(
    everything_in(extras),
    get_reqs("dev"),
)

if not PY34:
    extras["dev"] = unique_wrt(extras["dev"], extras["mypy"])

if PURE_PYTHON:
    # override necessary for readthedocs
    requirements += get_reqs("purepython")
elif supports_env_markers:
    # modern method
    extras[":platform_python_implementation=='CPython'"] = get_reqs("cpython")
    extras[":platform_python_implementation!='CPython'"] = get_reqs("purepython")
else:
    # old method
    if CPYTHON:
        requirements += get_reqs("cpython")
    else:
        requirements += get_reqs("purepython")

if using_modern_setuptools:
    # modern method
    extras[":python_version<'2.7'"] = get_reqs("py26")
    extras[":python_version>='2.7'"] = get_reqs("non-py26")
    extras[":python_version<'3'"] = get_reqs("py2")
    extras[":python_version>='3'"] = get_reqs("py3")
else:
    # old method
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
    import requests  # expensive
    url = "https://pypi.python.org/pypi/" + get_base_req(req, include_extras=False) + "/json"
    for i, sleep_time in enumerate(requests_sleep_times):
        time.sleep(sleep_time)
        try:
            result = requests.get(url)
        except Exception:
            if i == len(requests_sleep_times) - 1:
                print("Error accessing:", url)
                raise
            elif i > 0:
                print("Error accessing:", url, "(retrying)")
        else:
            break
    try:
        return tuple(result.json()["releases"].keys())
    except Exception:
        if embed_on_internal_exc:
            traceback.print_exc()
            embed()
        raise


def newer(new_ver, old_ver, strict=False):
    """Determines if the first version tuple is newer than the second.
    True if newer; False if older."""
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
    pinned_updates = []
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
        if req in pinned_reqs:
            pinned_updates.append(update_str)
        elif new_versions:
            new_updates.append(update_str)
        elif same_versions:
            same_updates.append(update_str)
    print("\n".join(new_updates))
    print()
    print("\n".join(same_updates))
    print()
    print("\n".join(pinned_updates))


if __name__ == "__main__":
    print_new_versions()
