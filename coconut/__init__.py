#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
The Coconut Programming Language
Copyright (c) 2015-2018 Evan Hubinger

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

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from coconut.constants import author as __author__  # NOQA

__version__ = VERSION  # NOQA

# -----------------------------------------------------------------------------------------------------------------------
# IPYTHON:
# -----------------------------------------------------------------------------------------------------------------------


def embed(kernel=False, depth=0, **kwargs):
    """If _kernel_=False (default), embeds a Coconut Jupyter console
    initialized from the current local namespace. If _kernel_=True,
    launches a Coconut Jupyter kernel initialized from the local
    namespace that can then be attached to. _kwargs_ are as in
    IPython.embed or IPython.embed_kernel based on _kernel_."""
    from coconut.icoconut.embed import embed, embed_kernel, extract_module_locals
    if kernel:
        mod, locs = extract_module_locals(1 + depth)
        embed_kernel(module=mod, local_ns=locs, **kwargs)
    else:
        embed(stack_depth=3 + depth, **kwargs)


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
