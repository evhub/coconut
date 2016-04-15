#!/usr/bin/env python

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

from ..command import *
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from ipykernel.kernelbase import Kernel

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------

class fakefile(StringIO):
    """A file-like object wrapper around a messaging function."""
    encoding = default_encoding # from ..compiler

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

#-----------------------------------------------------------------------------------------------------------------------
# KERNEL:
#-----------------------------------------------------------------------------------------------------------------------

proc = processor(target="sys") # from ..compiler

class kernel(Kernel):
    """Jupyter kernel for Coconut."""
    _runner = None # current ..command.executor
    implementation = "icoconut"
    implementation_version = VERSION
    language = "coconut"
    language_version = VERSION
    banner = "Coconut " + VERSION_STR
    language_info = {
        "name": "coconut",
        "mimetype": "text/x-python3",
        "file_extension": code_ext,
        "codemirror_mode": {
            "name": "python",
            "version": 3.6
        },
        "pygments_lexer": "coconut",
        "help_links": [
            {
                "text": "Coconut Tutorial",
                "url": tutorial_url
            },
            {
                "text": "Coconut Documentation",
                "url": documentation_url
            }
        ]
    }

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
            self._runner = executor(proc)

    def _execute(self, code, evaluate=False):
        """Compiles and runs code."""
        self._setup()
        try:
            if evaluate:
                compiled = proc.parse_eval(code)
            else:
                compiled = proc.parse_block(code)
        except CoconutException:
            printerr(get_error())
            return None
        else:
            if evaluate:
                return self._runner.run(compiled, run_func=eval)
            else:
                return self._runner.run(compiled)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
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
            proc.parse_block(code)
        except CoconutException:
            if code.endswith("\n\n"):
                return {
                    "status": "complete"
                }
            elif proc.should_indent(code):
                return {
                    "status": "incomplete",
                    "indent": " "*tabideal
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
        obj_name = ""
        for i in reversed(range(cursor_pos)):
            c = code[i]
            if c in alphanums:
                obj_name = c + obj_name
            else:
                break
        for i in range(cursor_pos, len(code)):
            c = code[i]
            if c in alphanums:
                obj_name += c
            else:
                break
        if obj_name in self._runner.vars and hasattr(self._runner.vars[obj_name], "__doc__"):
            return {
                "status": "ok",
                "found": True,
                "data": {
                    "text/plain": str(self._runner.vars[obj_name].__doc__)
                }
            }
        else:
            return {
                "status": "aborted",
                "found": False,
                "data": {}
            }
