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
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "coconut"))

from root import *
import setuptools

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

with open("README.rst", "r") as opened:
    readme = opened.read()

setuptools.setup(
    name = "coconut",
    version = VERSION,
    description = "Simple, elegant, Pythonic functional programming.",
    long_description = readme,
    url = "https://github.com/evhub/coconut",
    author = "Evan Hubinger",
    author_email = "evanjhub@gmail.com",
    classifiers = [
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
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
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Other",
        "Programming Language :: Other Scripting Engines",
        "Framework :: IPython",
        "Development Status :: 3 - Alpha"
        ],
    keywords = [
        "functional programming language",
        "functional programming",
        "functional",
        "programming language",
        "pattern-matching",
        "pattern matching",
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
        "curry"
        ],
    packages = setuptools.find_packages(),
    install_requires = [
        "pyparsing==2.0.5"
        ],
    entry_points = {"console_scripts":[
        "coconut = coconut.__main__:main"
        ]}
    )
