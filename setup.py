#!/usr/bin/env python

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

from coconut.root import *

import setuptools

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

extras = {
    "watch": "watchdog",
    "jupyter": "jupyter",
    "ipython": "jupyter",
}

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

#-----------------------------------------------------------------------------------------------------------------------
# README:
#-----------------------------------------------------------------------------------------------------------------------

with open("README.rst", "r") as readme_file:
    readme_lines = []
    in_toc = False
    for line in readme_file.readlines():
        if in_toc and line and not line.startswith(" "):
            in_toc = False
        if line == ".. toctree::":
            in_toc = True
        if not in_toc:
            readme_lines.append(line)
    readme = "\n".join(readme_lines)

#-----------------------------------------------------------------------------------------------------------------------
# REQUIREMENTS:
#-----------------------------------------------------------------------------------------------------------------------

def read_reqs(req_file):
    return [line.strip() for line in req_file.readlines() if line]

with open("requirements.txt", "r") as req_file:
    reqs = read_reqs(req_file)

with open("requirements-py2.txt", "r") as req_py2_file:
    py2_reqs = read_reqs(req_py2_file)

if PY2:
    reqs += py2_reqs

PY26 = sys.version_info < (2, 7)

with open("requirements-py26.txt", "r") as req_py26_file:
    py26_reqs = read_reqs(req_py26_file)

if PY26:
    reqs += py26_reqs
py26_reqs += py2_reqs

extras["all"] = list(set(extras.keys()))

if not PY2:
    extras["py2"] = py26_reqs
    extras["py27"] = py2_reqs

with open("requirements-docs.txt", "r") as req_docs_file:
    extras["docs"] = read_reqs(req_docs_file)

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

setuptools.setup(
    name = "coconut",
    version = VERSION,
    description = "Simple, elegant, Pythonic functional programming.",
    long_description = readme,
    url = "http://coconut-lang.org",
    author = "Evan Hubinger",
    author_email = "evanjhub@gmail.com",
    install_requires = reqs,
    extras_require = extras,
    packages = setuptools.find_packages(),
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "coconut = coconut.__main__:main",
            ],
        "pygments.lexers": [
            "coconut_python = coconut.highlighter:pylexer",
            "coconut_pycon = coconut.highlighter:pyconlexer",
            "coconut = coconut.highlighter:cocolexer",
            ]
        },
    classifiers = classifiers,
    keywords = search_terms,
    )
