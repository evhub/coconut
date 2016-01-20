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

import sys
import os.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coconut.command import *
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from ipykernel.kernelbase import Kernel

#-----------------------------------------------------------------------------------------------------------------------
# KERNEL:
#-----------------------------------------------------------------------------------------------------------------------

proc = processor(version="2" if PY2 else "3")
runner = executor(proc.headers("code"))

class kernel(Kernel):
    implementation = "icoconut"
    implementation_version = VERSION
    language = "coconut"
    language_version = VERSION
    banner = "Coconut Interpreter:"
    language_info = {
        "mimetype": "text/x-python",
        "file_extension": ".coc",
        "codemirror_mode": "python",
        "pygments_lexer": "python"
    }

    def _send(self, silent, text, debug=False):
        if not silent:
            message = {
                "name": "stderr" if debug else "stdout",
                "text": text
                }
            self.send_response(self.iopub_socket, "stream", message)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if silent:
            store_history = False
        sys.stdout, stdout = StringIO(), sys.stdout
        try:
            runner.run(proc.parse_single(code))
        except CoconutException:
            self._send(silent, get_error(), True)
        finally:
            self._send(silent, sys.stdout.getvalue())
            sys.stdout.close()
            sys.stdout = stdout
        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": user_expressions if user_expressions is not None else {}
        }

    def do_is_complete(self, code):
        try:
            proc.parse_single(code)
        except CoconutException:
            return {
                "status": "incomplete",
                "indent": "    "
            }
        else:
            return {
                "status": "complete",
                "indent": "    "
            }
