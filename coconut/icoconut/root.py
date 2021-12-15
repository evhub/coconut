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
import sys

try:
    import asyncio
except ImportError:
    asyncio = None

from coconut.exceptions import (
    CoconutException,
    CoconutInternalException,
)
from coconut.constants import (
    WINDOWS,
    PY38,
    py_syntax_version,
    mimetype,
    version_banner,
    tutorial_url,
    documentation_url,
    code_exts,
    conda_build_env_var,
    coconut_kernel_kwargs,
)
from coconut.terminal import (
    logger,
    internal_assert,
)
from coconut.util import override
from coconut.compiler import Compiler
from coconut.compiler.util import should_indent
from coconut.command.util import Runner

if WINDOWS and PY38 and asyncio is not None:  # attempt to fix zmq warning
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    from IPython.core.inputsplitter import IPythonInputSplitter
    from IPython.core.interactiveshell import InteractiveShellABC
    from IPython.core.compilerop import CachingCompiler
    from IPython.terminal.embed import InteractiveShellEmbed
    from ipykernel.ipkernel import IPythonKernel
    from ipykernel.zmqshell import ZMQInteractiveShell
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    LOAD_MODULE = False
    if os.environ.get(conda_build_env_var):
        # conda tries to import coconut.icoconut as a test even when IPython isn't available
        logger.warn("Missing IPython but detected " + conda_build_env_var + "; skipping coconut.icoconut loading")
    else:
        raise CoconutException(
            "--jupyter flag requires Jupyter library",
            extra="run '{python} -m pip install coconut[jupyter]' to fix".format(python=sys.executable),
        )
else:
    LOAD_MODULE = True


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------

COMPILER = Compiler(**coconut_kernel_kwargs)

RUNNER = Runner(COMPILER)

parse_block_memo = {}


def memoized_parse_block(code):
    """Memoized version of parse_block."""
    internal_assert(lambda: code not in parse_block_memo.values(), "attempted recompilation of", code)
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


def syntaxerr_memoized_parse_block(code):
    """Version of memoized_parse_block that raises SyntaxError without any __cause__."""
    to_raise = None
    try:
        return memoized_parse_block(code)
    except CoconutException as err:
        to_raise = err.syntax_err()
    raise to_raise


# -----------------------------------------------------------------------------------------------------------------------
# KERNEL:
# -----------------------------------------------------------------------------------------------------------------------

if LOAD_MODULE:

    COMPILER.warm_up()

    class CoconutCompiler(CachingCompiler, object):
        """IPython compiler for Coconut."""

        def __init__(self):
            super(CoconutCompiler, self).__init__()

            # we compile the header here to cache the proper __future__ imports
            header = COMPILER.getheader("sys")
            super(CoconutCompiler, self).__call__(header, "<string>", "exec")

        @override
        def ast_parse(self, source, *args, **kwargs):
            """Version of ast_parse that compiles Coconut code first."""
            compiled = syntaxerr_memoized_parse_block(source)
            return super(CoconutCompiler, self).ast_parse(compiled, *args, **kwargs)

        @override
        def cache(self, code, *args, **kwargs):
            """Version of cache that compiles Coconut code first."""
            try:
                compiled = memoized_parse_block(code)
            except CoconutException:
                logger.print_exc()
                return None
            else:
                return super(CoconutCompiler, self).cache(compiled, *args, **kwargs)

        @override
        def __call__(self, source, *args, **kwargs):
            """Version of __call__ that compiles Coconut code first."""
            if isinstance(source, (str, bytes)):
                compiled = syntaxerr_memoized_parse_block(source)
            else:
                compiled = source
            return super(CoconutCompiler, self).__call__(compiled, *args, **kwargs)

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

    INTERACTIVE_SHELL_CODE = '''
input_splitter = CoconutSplitter(line_input_checker=True)
input_transformer_manager = CoconutSplitter(line_input_checker=False)

@override
def init_instance_attrs(self):
    """Version of init_instance_attrs that uses CoconutCompiler."""
    super({cls}, self).init_instance_attrs()
    self.compile = CoconutCompiler()

@override
def init_user_ns(self):
    """Version of init_user_ns that adds Coconut built-ins."""
    super({cls}, self).init_user_ns()
    RUNNER.update_vars(self.user_ns)
    RUNNER.update_vars(self.user_ns_hidden)

@override
def run_cell(self, raw_cell, store_history=False, silent=False, shell_futures=True, **kwargs):
    """Version of run_cell that always uses shell_futures."""
    return super({cls}, self).run_cell(raw_cell, store_history, silent, shell_futures=True, **kwargs)

if asyncio is not None:
    @override
    @asyncio.coroutine
    def run_cell_async(self, raw_cell, store_history=False, silent=False, shell_futures=True, **kwargs):
        """Version of run_cell_async that always uses shell_futures."""
        return super({cls}, self).run_cell_async(raw_cell, store_history, silent, shell_futures=True, **kwargs)

@override
def user_expressions(self, expressions):
    """Version of user_expressions that compiles Coconut code first."""
    compiled_expressions = {dict}
    for key, expr in expressions.items():
        try:
            compiled_expressions[key] = COMPILER.parse_eval(expr)
        except CoconutException:
            compiled_expressions[key] = expr
    return super({cls}, self).user_expressions(compiled_expressions)
'''

    class CoconutShell(ZMQInteractiveShell, object):
        """ZMQInteractiveShell for Coconut."""
        exec(INTERACTIVE_SHELL_CODE.format(dict="{}", cls="CoconutShell"))

    InteractiveShellABC.register(CoconutShell)

    class CoconutShellEmbed(InteractiveShellEmbed, object):
        """InteractiveShellEmbed for Coconut."""
        exec(INTERACTIVE_SHELL_CODE.format(dict="{}", cls="CoconutShellEmbed"))

    InteractiveShellABC.register(CoconutShellEmbed)

    class CoconutKernel(IPythonKernel, object):
        """Jupyter kernel for Coconut."""
        shell_class = CoconutShell
        use_experimental_completions = True
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

        @override
        def do_complete(self, code, cursor_pos):
            # first try with Jedi completions
            self.use_experimental_completions = True
            try:
                return super(CoconutKernel, self).do_complete(code, cursor_pos)
            except Exception:
                logger.print_exc()
                logger.warn_err(CoconutInternalException("experimental IPython completion failed, defaulting to shell completion"), force=True)

            # then if that fails default to shell completions
            self.use_experimental_completions = False
            try:
                return super(CoconutKernel, self).do_complete(code, cursor_pos)
            finally:
                self.use_experimental_completions = True

    class CoconutKernelApp(IPKernelApp, object):
        """IPython kernel app that uses the Coconut kernel."""
        name = "coconut-kernel"
        classes = IPKernelApp.classes + [CoconutKernel, CoconutShell]
        kernel_class = CoconutKernel
        subcommands = {}
