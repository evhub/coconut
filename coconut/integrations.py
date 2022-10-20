#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Endpoints for Coconut's external integrations.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from types import MethodType

from coconut.constants import (
    coconut_kernel_kwargs,
    max_xonsh_cmd_len,
)

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
    from coconut import convenience
    from coconut.exceptions import CoconutException
    from coconut.terminal import logger

    magic_state = convenience.get_state()
    convenience.setup(state=magic_state, **coconut_kernel_kwargs)

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
                    convenience.cmd(line, default_target="sys", state=magic_state)
                code = cell
            compiled = convenience.parse(code, state=magic_state)
        except CoconutException:
            logger.print_exc()
        else:
            ipython.run_cell(compiled, shell_futures=False)
    ipython.register_magic_function(magic, "line_cell", "coconut")


# -----------------------------------------------------------------------------------------------------------------------
# XONSH:
# -----------------------------------------------------------------------------------------------------------------------

def _load_xontrib_(xsh, **kwargs):
    """Special function to load the Coconut xontrib."""
    # hide imports to avoid circular dependencies
    from coconut.exceptions import CoconutException
    from coconut.terminal import format_error
    from coconut.compiler import Compiler
    from coconut.command.util import Runner

    COMPILER = Compiler(**coconut_kernel_kwargs)
    COMPILER.warm_up()

    RUNNER = Runner(COMPILER)

    RUNNER.update_vars(xsh.ctx)

    def new_parse(self, s, *args, **kwargs):
        """Coconut-aware version of xonsh's _parse."""
        err_str = None
        if len(s) > max_xonsh_cmd_len:
            err_str = "Coconut disabled on commands of len > {max_xonsh_cmd_len} for performance reasons".format(max_xonsh_cmd_len=max_xonsh_cmd_len)
        else:
            try:
                s = COMPILER.parse_xonsh(s)
            except CoconutException as err:
                err_str = format_error(err).splitlines()[0]
        if err_str is not None:
            s += " # " + err_str
        return self.__class__.parse(self, s, *args, **kwargs)

    main_parser = xsh.execer.parser
    main_parser.parse = MethodType(new_parse, main_parser)

    ctx_parser = xsh.execer.ctxtransformer.parser
    ctx_parser.parse = MethodType(new_parse, ctx_parser)

    return RUNNER.vars
