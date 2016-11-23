#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: The Coconut IPython kernel.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from ipykernel.ipkernel import IPythonKernel
from ipykernel.zmqshell import ZMQInteractiveShell
from IPython.core.inputsplitter import IPythonInputSplitter
from IPython.core.interactiveshell import InteractiveShellABC
from IPython.core.compilerop import CachingCompiler

from coconut.exceptions import CoconutException
from coconut.constants import (
    py_syntax_version,
    mimetype,
    version_banner,
    tutorial_url,
    documentation_url,
    code_exts,
)
from coconut.compiler import Compiler
from coconut.command.util import Runner

#-----------------------------------------------------------------------------------------------------------------------
# GLOBALS:
#-----------------------------------------------------------------------------------------------------------------------

COMPILER = Compiler(target="sys")
RUNNER = Runner(COMPILER)


def PARSE(code):
    """Memoized COMPILER.parse_block."""
    try:
        compiled = COMPILER.parse_block(code)
    except CoconutException as err:
        raise err.syntax_err()
    else:
        return compiled

#-----------------------------------------------------------------------------------------------------------------------
# KERNLE:
#-----------------------------------------------------------------------------------------------------------------------


class CoconutCompiler(CachingCompiler):
    """IPython compiler for Coconut."""

    def __init__(self, *args, **kwargs):
        """Version of __init__ that remembers header futures."""
        super(CoconutCompiler, self).__init__(*args, **kwargs)
        super(CoconutCompiler, self).ast_parse(COMPILER.getheader("sys"))

    def ast_parse(self, source, *args, **kwargs):
        """Version of ast_parse that compiles Coconut code first."""
        compiled = PARSE(source)
        return super(CoconutCompiler, self).ast_parse(compiled, *args, **kwargs)


class CoconutSplitter(IPythonInputSplitter):
    """IPython splitter for Coconut."""

    def __init__(self, *args, **kwargs):
        """Version of __init__ that sets up Coconut code compilation."""
        super(CoconutSplitter, self).__init__(*args, **kwargs)
        self._python_compile = self._compile

        def _compile(source, *args, **kwargs):
            compiled = PARSE(source)
            return self._python_compile(compiled)
        self._compile = _compile


class CoconutShell(ZMQInteractiveShell):
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
        return super(CoconutShell, self).run_cell(raw_cell, store_history, silent)


InteractiveShellABC.register(CoconutShell)


class CoconutKernel(IPythonKernel):
    """Jupyter kernel for Coconut."""
    shell_class = CoconutShell
    implementation = "icoconut"
    implementation_version = VERSION
    language = "coconut"
    language_version = VERSION
    banner = version_banner
    language_info = {
        "name": "coconut",
        "mimetype": mimetype,
        "file_extension": code_exts[0],
        "codemirror_mode": {
            "name": "python",
            "version": py_syntax_version
        },
        "pygments_lexer": "coconut"
    }
    help_links = [
        {
            "text": "Coconut Tutorial",
            "url": tutorial_url
        },
        {
            "text": "Coconut Documentation",
            "url": documentation_url
        }
    ]
