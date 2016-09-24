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

import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from ipykernel.kernelbase import Kernel

from coconut.command import Runner
from coconut.compiler import Compiler
from coconut.exceptions import CoconutException
from coconut.logging import logger
from coconut.constants import (
    py_syntax_version,
    mimetype,
    varchars,
    all_keywords,
    version_banner,
    tutorial_url,
    documentation_url,
    reserved_prefix,
    default_encoding,
    code_exts,
    tabideal,
)

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


class fakefile(StringIO):
    """A file-like object wrapper around a messaging function."""
    encoding = default_encoding  # from coconut.compiler

    def __init__(self, send):
        """Initialize with a messaging function."""
        StringIO.__init__(self)
        self._send = send

    def _refresh(self):
        """Send value to the messaging function."""
        self._send(self.getvalue())
        self.seek(0)
        self.truncate()

    def flush(self, *args, **kwargs):
        """Flush to the messaging function."""
        StringIO.flush(self, *args, **kwargs)
        self._refresh()

    def write(self, *args, **kwargs):
        """Write to the messaging function."""
        StringIO.write(self, *args, **kwargs)
        self._refresh()

    def writelines(self, *args, **kwargs):
        """Write lines to the messaging function."""
        StringIO.writelines(self, *args, **kwargs)
        self._refresh()


def get_name(code, cursor_pos, get_bounds=False):
    """Extract the name of the object in code at cursor_pos."""
    name, left, right = "", cursor_pos, cursor_pos + 1
    i = None
    for i in reversed(range(cursor_pos)):
        c = code[i]
        if c in varchars:
            name = c + name
        else:
            left = i + 1
            break
    if i == 0:
        left = 0
    i = None
    for i in range(cursor_pos, len(code)):
        c = code[i]
        if c in varchars:
            name += c
        else:
            right = i
            break
    if i == len(code) - 1:
        right = len(code)
    if get_bounds:
        return name, left, right
    else:
        return name

#-----------------------------------------------------------------------------------------------------------------------
# KERNEL:
#-----------------------------------------------------------------------------------------------------------------------

comp = Compiler(target="sys")  # from coconut.compiler


class CoconutKernel(Kernel):
    """Jupyter kernel for Coconut."""
    _runner = None  # current ..command.Runner
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

    def _send(self, silent, text, debug=False):
        """Send message to console."""
        if not silent:
            message = {
                "name": "stderr" if debug else "stdout",
                "text": text
            }
            self.send_response(self.iopub_socket, "stream", message)

    def _setup(self, force=False):
        """Binds to the runner."""
        if force or self._runner is None:
            self._runner = Runner(comp)

    def _execute(self, code, use_eval=None):
        """Compiles and runs code."""
        self._setup()
        try:
            if use_eval:
                compiled = comp.parse_eval(code)
            else:
                compiled = comp.parse_block(code)
        except CoconutException:
            logger.print_exc()
            return None
        else:
            return self._runner.run(compiled, use_eval=use_eval)

    def do_execute(self, code, silent=False, store_history=True, user_expressions=None, allow_stdin=False):
        """Execute Coconut code."""
        if silent:
            store_history = False
        if user_expressions is None:
            user_expressions = {}

        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = fakefile(lambda text: self._send(silent, text))
        sys.stderr = fakefile(lambda text: self._send(silent, text, True))

        self._execute(code)
        for name in user_expressions:
            user_expressions[name] = self._execute(user_expressions[name], True)

        sys.stdout.close()
        sys.stderr.close()
        sys.stdout, sys.stderr = stdout, stderr
        if not store_history:
            self._setup(True)
        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "user_expressions": user_expressions
        }

    def do_is_complete(self, code):
        """Check Coconut code for correctness."""
        try:
            comp.parse_block(code)
        except CoconutException:
            if code.endswith("\n"):
                return {
                    "status": "complete"
                }
            elif comp.should_indent(code):
                return {
                    "status": "incomplete",
                    "indent": " " * tabideal
                }
            else:
                return {
                    "status": "incomplete"
                }
        else:
            return {
                "status": "complete"
            }

    def do_inspect(self, code, cursor_pos, detail_level=0):
        """Gets information on an object."""
        self._setup()
        test_name = get_name(code, cursor_pos)
        if test_name in self._runner.vars and hasattr(self._runner.vars[test_name], "__doc__"):
            return {
                "status": "ok",
                "found": True,
                "data": {
                    "text/plain": str(self._runner.vars[test_name].__doc__)
                }
            }
        else:
            return {
                "status": "aborted",
                "found": False,
                "data": {}
            }

    def do_complete(self, code, cursor_pos):
        """Completes code at position."""
        self._setup()
        test_name, cursor_start, cursor_end = get_name(code, cursor_pos, True)
        matches = []
        if cursor_start > 1 and code[cursor_start - 1] == "." and code[cursor_start - 2] in varchars:
            obj_name = get_name(code, cursor_start - 1)
            if obj_name in self._runner.vars:
                for var_name in dir(self._runner.vars[obj_name]):
                    if var_name.startswith(test_name) and not var_name.startswith(reserved_prefix):
                        matches.append(var_name)
        else:
            for var_name in tuple(self._runner.vars) + all_keywords:
                if var_name.startswith(test_name) and not var_name.startswith(reserved_prefix):
                    matches.append(var_name)
        return {
            "status": "ok",
            "matches": list(sorted(matches)),
            "cursor_start": cursor_start,
            "cursor_end": cursor_end,
            "metadata": {}
        }
