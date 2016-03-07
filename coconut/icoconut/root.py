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
    encoding = encoding

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

proc = processor(version="2" if PY2 else "3")

class kernel(Kernel):
    """Jupyter kernel for Coconut."""
    _runner = None
    implementation = "icoconut"
    implementation_version = VERSION
    language = "coconut"
    language_version = VERSION
    banner = "Coconut"
    language_info = {
        "name": "coconut",
        "mimetype": "text/x-python3",
        "file_extension": code_ext,
        "codemirror_mode": "python",
        "pygments_lexer": "coconut"
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
        if self._runner is None or force:
            self._runner = executor(proc.headers("code"))

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
                return self._runner.run(compiled, dorun=eval)
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
                    "indent": " "*tablen
                }
            else:
                return {
                    "status": "incomplete"
                }
        else:
            return {
                "status": "complete"
            }
