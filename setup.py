#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Installer for the Coconut Programming Language.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coconut.root import *  # NOQA

import setuptools
import platform

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: Apache Software License",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Topic :: Software Development",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Compilers",
    "Topic :: Software Development :: Interpreters",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Other",
    "Programming Language :: Other Scripting Engines",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Framework :: IPython",
]

search_terms = [
    "functional programming language",
    "functional programming",
    "functional",
    "programming language",
    "compiler",
    "match",
    "matches",
    "matching",
    "pattern-matching",
    "pattern matching",
    "algebraic data type",
    "algebraic data types",
    "data",
    "data type",
    "data types",
    "lambda",
    "lambdas",
    "lazy list",
    "lazy lists",
    "lazy evaluation",
    "lazy",
    "tail recursion",
    "tail call",
    "optimization",
    "recursion",
    "recursive",
    "infix",
    "function composition",
    "partial application",
    "currying",
    "curry",
    "pipeline",
    "pipe",
    "unicode operator",
    "unicode operators",
    "frozenset literal",
    "frozenset literals",
    "destructuring",
    "destructuring assignment",
    "reduce",
    "takewhile",
    "dropwhile",
    "tee",
    "consume",
    "count",
    "parallel_map",
    "concurrent_map",
    "MatchError",
    "datamaker",
    "addpattern",
    "prepattern",
    "recursive_iterator",
    "data keyword",
    "match keyword",
    "case keyword",
]

script_names = [
    "coconut",
    "coconut-" + VERSION_TAG.split("-", 1)[0],
    ("coconut-py2" if PY2 else "coconut-py3"),
    "coconut-py" + str(sys.version_info[0]) + str(sys.version_info[1]),
    ("coconut-develop" if DEVELOP else "coconut-release"),
]

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def read_reqs(tag=""):
    """Read the requirements file for the given tag."""
    if tag:
        tag = "-" + tag
    req_file_name = "./reqs/requirements" + tag + ".txt"
    with open(req_file_name, "r") as req_file:
        return [line.strip() for line in req_file.readlines() if line]


def uniqueify(reqs):
    """Make a list of requirements unique."""
    return list(set(reqs))


def unique_from(reqs, main_reqs):
    """Ensures reqs doesn't contain anything in main_reqs."""
    return list(set(reqs) - set(main_reqs))


def all_reqs_in(req_dict):
    """Gets all requirements in a requirements dict."""
    return uniqueify(req for req_list in req_dict.values() for req in req_list)

#-----------------------------------------------------------------------------------------------------------------------
# REQUIREMENTS:
#-----------------------------------------------------------------------------------------------------------------------

requirements = read_reqs()

if PY26:
    requirements += read_reqs("py26")
else:
    requirements += read_reqs("non-py26")

if PY2:
    requirements += read_reqs("py2")

extras = {
    "watch": read_reqs("watch"),
    "jobs": read_reqs("jobs"),
    "mypy": read_reqs("mypy"),
}

extras["jupyter"] = extras["ipython"] = read_reqs("jupyter")

extras["all"] = all_reqs_in(extras)

extras["tests"] = uniqueify(
    read_reqs("tests")
    + (extras["jobs"] if platform.python_implementation() != "PyPy" else [])
    + (extras["jupyter"] if (PY2 and not PY26) or sys.version_info >= (3, 3) else [])
    + (extras["mypy"] if not PY2 else [])
)

extras["docs"] = unique_from(read_reqs("docs"), requirements)

extras["dev"] = uniqueify(
    all_reqs_in(extras)
    + read_reqs("dev")
)

#-----------------------------------------------------------------------------------------------------------------------
# README:
#-----------------------------------------------------------------------------------------------------------------------

with open("README.rst", "r") as readme_file:
    readme_lines = []
    in_toc = False
    for line in readme_file.readlines():
        if line.startswith(".. toctree::"):
            in_toc = True
        elif in_toc and 0 < len(line.lstrip()) == len(line):
            in_toc = False
        if not in_toc:
            readme_lines.append(line)
    readme = "".join(readme_lines)

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

setuptools.setup(
    name="coconut" + ("-develop" if DEVELOP else ""),
    version=VERSION,
    description="Simple, elegant, Pythonic functional programming.",
    long_description=readme,
    url="http://coconut-lang.org",
    author="Evan Hubinger",
    author_email="evanjhub@gmail.com",
    install_requires=requirements,
    extras_require=extras,
    packages=setuptools.find_packages(exclude=[
        "reqs",
        "docs",
        "tests",
    ]),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            script + " = coconut.main:main"
            for script in script_names
        ] + [
            script + "-run = coconut.main:main_run"
            for script in script_names
        ],
        "pygments.lexers": [
            "coconut = coconut.highlighter:CoconutLexer",
            "coconut_python = coconut.highlighter:CoconutPythonLexer",
            "coconut_pycon = coconut.highlighter:CoconutPythonConsoleLexer",
        ]
    },
    classifiers=classifiers,
    keywords=search_terms,
)
