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

from coconut.constants import coconut_kernel_kwargs

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

class CoconutXontribLoader(object):
    """Implements Coconut's _load_xontrib_."""
    timing_info = []
    compiler = None
    runner = None

    def __call__(self, xsh, **kwargs):
        # hide imports to avoid circular dependencies
        from coconut.exceptions import CoconutException
        from coconut.terminal import format_error
        from coconut.util import get_clock_time

        start_time = get_clock_time()

        if self.compiler is None:
            from coconut.compiler import Compiler
            self.compiler = Compiler(**coconut_kernel_kwargs)
            self.compiler.warm_up()

        if self.runner is None:
            from coconut.command.util import Runner
            self.runner = Runner(self.compiler)

        self.runner.update_vars(xsh.ctx)

        def new_parse(execer, s, *args, **kwargs):
            """Coconut-aware version of xonsh's _parse."""
            parse_start_time = get_clock_time()
            try:
                s = self.compiler.parse_xonsh(s, keep_state=True)
            except CoconutException as err:
                err_str = format_error(err).splitlines()[0]
                s += " #" + err_str
            self.timing_info.append(("parse", get_clock_time() - parse_start_time))
            return execer.__class__.parse(execer, s, *args, **kwargs)

        main_parser = xsh.execer.parser
        main_parser.parse = MethodType(new_parse, main_parser)

        ctx_parser = xsh.execer.ctxtransformer.parser
        ctx_parser.parse = MethodType(new_parse, ctx_parser)

        self.timing_info.append(("load", get_clock_time() - start_time))

        return self.runner.vars


_load_xontrib_ = CoconutXontribLoader()
