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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "coconut"))

from root import *
import setuptools

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

with open("README.rst", "r") as readme_file:
    readme_lines = []
    in_toc = False
    for line in readme_file.readlines():
        line = line.rstrip()
        if in_toc and line and not line.startswith(" "):
            in_toc = False
        if line == ".. toctree::":
            in_toc = True
        if not in_toc:
            readme_lines.append(line)
    readme = "\n".join(readme_lines)

setuptools.setup(
    name = "coconut",
    version = VERSION,
    description = "Simple, elegant, Pythonic functional programming.",
    long_description = readme,
    url = "http://coconut-lang.org",
    author = "Evan Hubinger",
    author_email = "evanjhub@gmail.com",
    install_requires = [
        "pyparsing==2.1.5"
        ],
    extras_require = {
        "all": [
            "autopep8",
            "watchdog"
        ],
        "autopep8": "autopep8",
        "watch": "watchdog"
    },
    packages = setuptools.find_packages(),
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "coconut = coconut.__main__:main"
            ],
        "pygments.lexers": [
            "coconut_python = coconut.highlighter:pylexer",
            "coconut_pycon = coconut.highlighter:pyconlexer",
            "coconut = coconut.highlighter:cocolexer"
            ]
        },
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
        "Framework :: IPython"
        ],
    keywords = [
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
        "MatchError",
        "datamaker",
        "data keyword",
        "match keyword",
        "case keyword"
        ]
    )
