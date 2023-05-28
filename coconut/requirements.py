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

from coconut.integrations import embed
from coconut.constants import (
    CPYTHON,
    PY34,
    IPY,
    MYPY,
    XONSH,
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
    assert_remove_prefix,
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


def process_mark(mark):
    """Get the check string and whether it currently applies for the given mark."""
    assert not mark.startswith("py2"), "confusing mark; should be changed: " + mark
    if mark.startswith("py=="):
        ver = assert_remove_prefix(mark, "py==")
        if len(ver) == 1:
            ver_tuple = (int(ver),)
        else:
            ver_tuple = (int(ver[0]), int(ver[1:]))
        next_ver_tuple = get_next_version(ver_tuple)
        check_str = (
            "python_version>='" + ver_tuple_to_str(ver_tuple) + "'"
            + " and python_version<'" + ver_tuple_to_str(next_ver_tuple) + "'"
        )
        holds_now = (
            sys.version_info >= ver_tuple
            and sys.version_info < next_ver_tuple
        )
    elif mark in ("py3", "py>=3"):
        check_str = "python_version>='3'"
        holds_now = not PY2
    elif mark == "py<3":
        check_str = "python_version<'3'"
        holds_now = PY2
    elif mark.startswith("py<"):
        full_ver = assert_remove_prefix(mark, "py<")
        main_ver, sub_ver = full_ver[0], full_ver[1:]
        check_str = "python_version<'{main}.{sub}'".format(main=main_ver, sub=sub_ver)
        holds_now = sys.version_info < (int(main_ver), int(sub_ver))
    elif mark.startswith("py") or mark.startswith("py>="):
        full_ver = assert_remove_prefix(mark, "py")
        if full_ver.startswith(">="):
            full_ver = assert_remove_prefix(full_ver, ">=")
        main_ver, sub_ver = full_ver[0], full_ver[1:]
        check_str = "python_version>='{main}.{sub}'".format(main=main_ver, sub=sub_ver)
        holds_now = sys.version_info >= (int(main_ver), int(sub_ver))
    elif mark == "cpy":
        check_str = "platform_python_implementation=='CPython'"
        holds_now = CPYTHON
    elif mark == "windows":
        check_str = "os_name=='nt'"
        holds_now = WINDOWS
    elif mark.startswith("mark"):
        check_str = None
        holds_now = True
    else:
        raise ValueError("unknown env marker " + repr(mark))
    return check_str, holds_now


def get_req_str(req):
    """Get the str that properly versions the given req."""
    req_str = get_base_req(req) + ">=" + ver_tuple_to_str(min_versions[req])
    if req in max_versions:
        max_ver = max_versions[req]
        if max_ver is None:
            max_ver = get_next_version(min_versions[req])
        if None in max_ver:
            assert all(v is None for v in max_ver), "invalid max version " + repr(max_ver)
            max_ver = get_next_version(min_versions[req], len(max_ver) - 1)
        req_str += ",<" + ver_tuple_to_str(max_ver)
    return req_str


def get_env_markers(req):
    """Get the environment markers for the given req."""
    if isinstance(req, tuple):
        return req[1].split(";")
    else:
        return ()


def get_reqs(which):
    """Gets requirements from all_reqs with versions."""
    reqs = []
    for req in all_reqs[which]:
        req_str = get_req_str(req)
        use_req = True
        markers = []
        for mark in get_env_markers(req):
            check_str, holds_now = process_mark(mark)
            if supports_env_markers:
                if check_str is not None:
                    markers.append(check_str)
            else:
                if not holds_now:
                    use_req = False
                    break
        if markers:
            req_str += ";" + " and ".join(markers)
        if use_req:
            reqs.append(req_str)
    return reqs


def get_main_reqs(main_reqs_name):
    """Get the main requirements and extras."""
    requirements = []
    extras = {}
    if using_modern_setuptools:
        for req in all_reqs[main_reqs_name]:
            req_str = get_req_str(req)
            markers = []
            for mark in get_env_markers(req):
                check_str, _ = process_mark(mark)
                if check_str is not None:
                    markers.append(check_str)
            if markers:
                extras.setdefault(":" + " and ".join(markers), []).append(req_str)
            else:
                requirements.append(req_str)
    else:
        requirements += get_reqs(main_reqs_name)
    return requirements, extras


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

requirements, reqs_extras = get_main_reqs("main")

extras = {
    "kernel": get_reqs("kernel"),
    "watch": get_reqs("watch"),
    "mypy": get_reqs("mypy"),
    "backports": get_reqs("backports"),
    "xonsh": get_reqs("xonsh"),
}

extras["jupyter"] = uniqueify_all(
    extras["kernel"],
    get_reqs("jupyter"),
)

extras["all"] = everything_in(extras)

extras.update({
    "ipython": extras["jupyter"],
    "docs": unique_wrt(get_reqs("docs"), requirements),
    "tests": uniqueify_all(
        get_reqs("tests"),
        extras["backports"],
        extras["jupyter"] if IPY else [],
        extras["mypy"] if MYPY else [],
        extras["xonsh"] if XONSH else [],
    ),
})

extras["dev"] = uniqueify_all(
    everything_in(extras),
    get_reqs("dev"),
)

if not PY34:
    extras["dev"] = unique_wrt(extras["dev"], extras["mypy"])

# has to come after dev so they don't get included in it
extras.update(reqs_extras)

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


def pretty_req(req):
    """Get a string representation of the given requirement."""
    if isinstance(req, tuple):
        base_req, env_marker = req
    else:
        base_req, env_marker = req, None
    return base_req + (" (" + env_marker + ")" if env_marker else "")


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
        update_str = (
            pretty_req(req)
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
