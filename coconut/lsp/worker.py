#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Compile worker: a child process that compiles Coconut code on request.

Protocol: one JSON object per line on stdin ({"id", "method", "params"}), one JSON response
per line on stdout ({"id", "result"} or {"id", "error"}).

Running compilation out of process keeps the language server responsive while Coconut's
(CPU-bound) parser runs, and lets the server kill and restart a compile that takes too long.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import json
import os
import subprocess
import sys
import threading
import traceback


def worker_main():
    out = sys.stdout
    sys.stdout = sys.stderr  # anything Coconut prints must not corrupt the protocol
    from coconut.lsp import compiler
    from coconut.lsp.compiler import compile_coconut, coconut_info
    compiler.USE_INCREMENTAL = True
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        response = {"id": msg.get("id")}
        try:
            method = msg.get("method")
            params = msg.get("params") or {}
            if method == "compile":
                response["result"] = compile_coconut(params.get("code", ""), params.get("settings"))
            elif method == "info":
                response["result"] = coconut_info()
            elif method == "warm_up":
                compile_coconut("x = 1 |> (+)$(1)\n", params.get("settings"))
                response["result"] = True
            else:
                response["error"] = "unknown method " + repr(method)
        except Exception:
            response["error"] = traceback.format_exc()
        out.write(json.dumps(response) + "\n")
        out.flush()


class CompileTimeout(Exception):
    pass


class WorkerClient(object):
    """Runs compile requests in a worker process, restarting it if it hangs or dies."""

    def __init__(self, python=None, timeout=60.0):
        self.python = python or sys.executable
        self.timeout = timeout
        self.proc = None
        self.lock = threading.Lock()
        self.next_id = 0

    def _start(self):
        # make sure the worker imports this same copy of Coconut (e.g. when running from a source checkout)
        package_parent = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env = dict(os.environ)
        env["PYTHONPATH"] = package_parent + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        env["PYTHONIOENCODING"] = "utf-8"
        self.proc = subprocess.Popen(
            [self.python, "-u", "-m", "coconut.lsp.worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            env=env,
            universal_newlines=True,
            encoding="utf-8",
            bufsize=1,
        )

    def _kill(self):
        if self.proc is not None:
            try:
                self.proc.kill()
                self.proc.wait(timeout=5)
            except Exception:
                pass
            self.proc = None

    def call(self, method, params=None, timeout=None):
        """Synchronously run a request in the worker. Raises CompileTimeout or RuntimeError."""
        timeout = self.timeout if timeout is None else timeout
        with self.lock:
            if self.proc is None or self.proc.poll() is not None:
                self._start()
            self.next_id += 1
            msg_id = self.next_id
            proc = self.proc
            try:
                proc.stdin.write(json.dumps({"id": msg_id, "method": method, "params": params or {}}) + "\n")
                proc.stdin.flush()
            except (OSError, ValueError):
                self._kill()
                raise RuntimeError("compile worker died")
            result = {}

            def read():
                try:
                    while True:
                        line = proc.stdout.readline()
                        if not line:
                            return
                        response = json.loads(line)
                        if response.get("id") == msg_id:
                            result["response"] = response
                            return
                except Exception:
                    result["exc"] = traceback.format_exc()

            reader = threading.Thread(target=read)
            reader.daemon = True
            reader.start()
            reader.join(timeout)
            if reader.is_alive():
                self._kill()
                raise CompileTimeout("compilation took longer than {t:g} seconds".format(t=timeout))
            response = result.get("response")
            if response is None:
                self._kill()
                raise RuntimeError("compile worker died" + (": " + result["exc"] if "exc" in result else ""))
            if "error" in response:
                raise RuntimeError(response["error"])
            return response["result"]

    def close(self):
        # don't wait for the lock: a compile may be running, and we want to exit promptly
        proc = self.proc
        if proc is not None:
            try:
                proc.stdin.close()
                proc.wait(timeout=2)
            except Exception:
                pass
            try:
                proc.kill()
            except Exception:
                pass


class InProcessCompiler(object):
    """Same interface as WorkerClient, but compiles in the current process (used by the CLI)."""

    def call(self, method, params=None, timeout=None):
        from coconut.lsp.compiler import compile_coconut, coconut_info
        params = params or {}
        if method == "compile":
            return compile_coconut(params.get("code", ""), params.get("settings"))
        if method == "info":
            return coconut_info()
        if method == "warm_up":
            return True
        raise RuntimeError("unknown method " + repr(method))

    def close(self):
        pass


if __name__ == "__main__":
    worker_main()
