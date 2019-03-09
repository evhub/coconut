#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: The Coconut IPython kernel.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import traceback

from coconut.exceptions import CoconutException
from coconut.constants import (
    py_syntax_version,
    mimetype,
    version_banner,
    tutorial_url,
    documentation_url,
    code_exts,
    conda_build_env_var,
)
from coconut.terminal import logger
from coconut.compiler import Compiler
from coconut.compiler.util import should_indent
from coconut.command.util import Runner

try:
    from IPython.core.inputsplitter import IPythonInputSplitter
    from IPython.core.interactiveshell import InteractiveShellABC
    from IPython.core.compilerop import CachingCompiler
    from ipykernel.ipkernel import IPythonKernel
    from ipykernel.zmqshell import ZMQInteractiveShell
except ImportError:
    LOAD_MODULE = False
    if os.environ.get(conda_build_env_var):
        # conda tries to import coconut.icoconut as a test even when IPython isn't available
        logger.warn("Missing IPython but detected " + conda_build_env_var + "; skipping coconut.icoconut loading")
    else:
        raise CoconutException(
            "--jupyter flag requires Jupyter library",
            extra="run 'pip install coconut[jupyter]' to fix",
        )
else:
    LOAD_MODULE = True

# -----------------------------------------------------------------------------------------------------------------------
# GLOBALS:
# -----------------------------------------------------------------------------------------------------------------------

COMPILER = Compiler(
    target="sys",
    line_numbers=True,
    keep_lines=True,
)

RUNNER = Runner(COMPILER)

parse_block_memo = {}


def memoized_parse_block(code):
    """Memoized version of parse_block."""
    success, result = parse_block_memo.get(code, (None, None))
    if success is None:
        try:
            parsed = COMPILER.parse_block(code)
        except Exception as err:
            success, result = False, err
        else:
            success, result = True, parsed
        parse_block_memo[code] = (success, result)
    if success:
        return result
    else:
        raise result


def memoized_parse_sys(code):
    """Memoized version of parse_sys."""
    return COMPILER.header_proc(memoized_parse_block(code), header="sys", initial="none")


# -----------------------------------------------------------------------------------------------------------------------
# KERNEL:
# -----------------------------------------------------------------------------------------------------------------------


if LOAD_MODULE:

    class CoconutCompiler(CachingCompiler, object):
        """IPython compiler for Coconut."""

        def ast_parse(self, source, *args, **kwargs):
            """Version of ast_parse that compiles Coconut code first."""
            try:
                compiled = memoized_parse_sys(source)
            except CoconutException as err:
                raise err.syntax_err()
            else:
                return super(CoconutCompiler, self).ast_parse(compiled, *args, **kwargs)

        def cache(self, code, *args, **kwargs):
            """Version of cache that compiles Coconut code first."""
            try:
                compiled = memoized_parse_sys(code)
            except CoconutException:
                traceback.print_exc()
                return None
            else:
                return super(CoconutCompiler, self).cache(compiled, *args, **kwargs)

    class CoconutSplitter(IPythonInputSplitter, object):
        """IPython splitter for Coconut."""

        def __init__(self, *args, **kwargs):
            """Version of __init__ that sets up Coconut code compilation."""
            super(CoconutSplitter, self).__init__(*args, **kwargs)
            self._compile = self._coconut_compile

        def _coconut_compile(self, source, *args, **kwargs):
            """Version of _compile that checks Coconut code.
            None means that the code should not be run as is.
            Any other value means that it can."""
            if source.endswith("\n\n"):
                return True
            elif should_indent(source):
                return None
            else:
                return True

    class CoconutShell(ZMQInteractiveShell, object):
        """IPython shell for Coconut."""
        input_splitter = CoconutSplitter(line_input_checker=True)
        input_transformer_manager = CoconutSplitter(line_input_checker=False)

        def init_instance_attrs(self):
            """Version of init_instance_attrs that uses CoconutCompiler."""
            super(CoconutShell, self).init_instance_attrs()
            self.compile = CoconutCompiler()

        def init_create_namespaces(self, *args, **kwargs):
            """Version of init_create_namespaces that adds Coconut built-ins to globals."""
            super(CoconutShell, self).init_create_namespaces(*args, **kwargs)
            RUNNER.update_vars(self.user_global_ns)

        def run_cell(self, raw_cell, store_history=False, silent=False, shell_futures=None):
            """Version of run_cell that always uses shell_futures."""
            return super(CoconutShell, self).run_cell(raw_cell, store_history, silent, shell_futures=True)

        def user_expressions(self, expressions):
            """Version of user_expressions that compiles Coconut code first."""
            compiled_expressions = {}
            for key, expr in expressions.items():
                try:
                    compiled_expressions[key] = COMPILER.parse_eval(expr)
                except CoconutException:
                    compiled_expressions[key] = expr
            return super(CoconutShell, self).user_expressions(compiled_expressions)

    InteractiveShellABC.register(CoconutShell)

    class CoconutKernel(IPythonKernel, object):
        """Jupyter kernel for Coconut."""
        shell_class = CoconutShell
        use_experimental_completions = False
        implementation = "icoconut"
        implementation_version = VERSION
        language = "coconut"
        language_version = VERSION
        banner = version_banner
        language_info = {
            "name": "coconut",
            "version": VERSION,
            "mimetype": mimetype,
            "codemirror_mode": {
                "name": "python",
                "version": py_syntax_version,
            },
            "pygments_lexer": "coconut",
            "file_extension": code_exts[0],
        }
        help_links = [
            {
                "text": "Coconut Tutorial",
                "url": tutorial_url,
            },
            {
                "text": "Coconut Documentation",
                "url": documentation_url,
            },
        ]
