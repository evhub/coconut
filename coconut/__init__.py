#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
The Coconut Programming Language
Copyright (c) 2015-2016 Evan Hubinger

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

#-----------------------------------------------------------------------------------------------------------------------
# IPYTHON:
#-----------------------------------------------------------------------------------------------------------------------


def load_ipython_extension(ipython):
    """Loads Coconut as an IPython extension."""
    from coconut.convenience import cmd, parse, CoconutException
    from coconut.logging import logger

    def magic(line, cell=None):
        """Coconut IPython magic."""
        try:
            if cell is None:
                code = line
            else:
                cmd(line)  # first line in block is cmd
                code = cell
            compiled = parse(code)
        except CoconutException:
            logger.print_exc()
        else:
            ipython.run_cell(compiled, shell_futures=False)
    ipython.register_magic_function(magic, "line_cell", "coconut")
