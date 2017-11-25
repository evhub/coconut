#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
The Coconut Programming Language
Copyright (c) 2015-2017 Evan Hubinger

Licensed under the Apache License, Version 2.0 (the "License");
you may not use these files except in compliance with the License.
You may obtain a copy of the License at:

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os.path

from coconut.constants import author as __author__  # NOQA
from coconut.constants import (
    code_exts,
    coconut_import_hook_args,
)

__version__ = VERSION  # NOQA

#-----------------------------------------------------------------------------------------------------------------------
# IPYTHON:
#-----------------------------------------------------------------------------------------------------------------------


def load_ipython_extension(ipython):
    """Loads Coconut as an IPython extension."""
    # add Coconut built-ins
    from coconut import __coconut__
    newvars = {}
    for var, val in vars(__coconut__).items():
        if not var.startswith("__"):
            newvars[var] = val
    ipython.push(newvars)

    # import here to avoid circular dependencies
    from coconut.convenience import cmd, parse, CoconutException
    from coconut.terminal import logger

    # add magic function
    def magic(line, cell=None):
        """Provides %coconut and %%coconut magics."""
        try:
            if cell is None:
                code = line
            else:
                # first line in block is cmd, rest is code
                line = line.strip()
                if line:
                    cmd(line, interact=False)
                code = cell
            compiled = parse(code)
        except CoconutException:
            logger.display_exc()
        else:
            ipython.run_cell(compiled, shell_futures=False)
    ipython.register_magic_function(magic, "line_cell", "coconut")


#-----------------------------------------------------------------------------------------------------------------------
# IMPORTER:
#-----------------------------------------------------------------------------------------------------------------------


class CoconutImporter(object):
    """Finder and loader for compiling Coconut files at import time."""

    def run_compiler(self, path):
        """Run the Coconut compiler on the given path."""
        # import here to avoid circular dependencies
        from coconut.convenience import cmd
        cmd([path] + list(coconut_import_hook_args))

    def find_module(self, fullname, path=None):
        """Searches for a Coconut file of the given name and compiles it."""
        basepaths = [""] + list(sys.path)
        if fullname.startswith("."):
            if path is None:
                # we can't do a relative import if there's no package path
                return None
            fullname = fullname[1:]
            basepaths.append(path)
        fullpath = os.path.join(*fullname.split("."))
        for head in basepaths:
            path = os.path.join(head, fullpath)
            for ext in code_exts:
                filepath = path + ext
                dirpath = os.path.join(path, "__init__" + ext)
                if os.path.exists(filepath):
                    self.run_compiler(filepath)
                    # Coconut file was found and compiled, now let Python import it
                    return None
                if os.path.exists(dirpath):
                    self.run_compiler(path)
                    # Coconut package was found and compiled, now let Python import it
                    return None
        return None


sys.meta_path.insert(0, CoconutImporter())
