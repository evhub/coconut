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
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------

def read_reqs(tag=""):
    if tag:
        tag = "-" + tag
    req_file_name = "./reqs/requirements" + tag + ".txt"
    with open(req_file_name, "r") as req_file:
        return [line.strip() for line in req_file.readlines() if line]

def all_reqs_in(req_dict):
    return list(set(req for req_list in req_dict.values() for req in req_list))

#-----------------------------------------------------------------------------------------------------------------------
# REQUIREMENTS:
#-----------------------------------------------------------------------------------------------------------------------

reqs = read_reqs()

if not PY26:
    reqs += read_reqs("non-py26")

if PY2:
    reqs += read_reqs("py2")
    if PY26:
        reqs += read_reqs("py26")

watch_reqs = read_reqs("watch")
jupyter_reqs = read_reqs("jupyter")
docs_reqs = read_reqs("docs")

extras = {
    "watch": watch_reqs,
    "jupyter": jupyter_reqs,
    "ipython": jupyter_reqs,
}

extras["all"] = all_reqs_in(extras)

extras["docs"] = docs_reqs

extras["dev"] = all_reqs_in(extras)

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
    packages = find_packages(exclude=[
        "reqs",
        "docs",
        "tests",
    ]),
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "coconut = coconut.main:main",
            ],
        "pygments.lexers": [
            "coconut = coconut.highlighter:CoconutLexer",
            "coconut_python = coconut.highlighter:CoconutPythonLexer",
            "coconut_pycon = coconut.highlighter:CoconutPythonConsoleLexer",
            ]
        },
    classifiers = classifiers,
    keywords = search_terms,
    )
