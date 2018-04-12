#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Installer for the Coconut Programming Language.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coconut.root import *  # NOQA

import setuptools

from coconut.constants import (
    package_name,
    author,
    author_email,
    description,
    website_url,
    classifiers,
    search_terms,
    script_names,
)
from coconut.requirements import (
    using_modern_setuptools,
    requirements,
    extras,
)

# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------

if not using_modern_setuptools and "bdist_wheel" in sys.argv:
    raise RuntimeError("bdist_wheel not supported for setuptools versions < 18 (run 'pip install --upgrade setuptools' to fix)")

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name=package_name,
    version=VERSION,
    description=description,
    long_description=readme,
    url=website_url,
    author=author,
    author_email=author_email,
    install_requires=requirements,
    extras_require=extras,
    packages=setuptools.find_packages(exclude=[
        "docs",
        "tests",
    ]),
    include_package_data=True,
    zip_safe=False,
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
        ],
    },
    classifiers=list(classifiers),
    keywords=list(search_terms),
)
