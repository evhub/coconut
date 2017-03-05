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

from coconut.constants import classifiers, search_terms, script_names
from coconut.requirements import requirements, extras

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
    document_names={
        "description": "README.rst",
        "license": "LICENSE.txt",
    },
    classifiers=classifiers,
    keywords=search_terms,
)
