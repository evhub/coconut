#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Minimal, dependency-free JSON-RPC 2.0 transport for the Language Server Protocol over stdio.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import json
import os
import sys
import threading
import traceback


# LSP error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SERVER_NOT_INITIALIZED = -32002
REQUEST_CANCELLED = -32800
REQUEST_FAILED = -32803


class ResponseError(Exception):
    """Raise from a request handler to send an error response."""

    def __init__(self, code, message, data=None):
        super(ResponseError, self).__init__(message)
        self.code = code
        self.message = message
        self.data = data


LOG_FILE = os.environ.get("COCONUT_LS_LOG")


def log(*args):
    """Log to stderr (stdout is reserved for protocol messages), and to $COCONUT_LS_LOG if set."""
    text = " ".join(str(a) for a in args) + "\n"
    try:
        sys.stderr.write(text)
        sys.stderr.flush()
    except Exception:
        pass
    if LOG_FILE:
        try:
            with open(LOG_FILE, "a") as f:
                f.write(text)
        except Exception:
            pass


class JsonRpcConnection(object):
    """Reads and writes LSP base-protocol framed JSON-RPC messages."""

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.write_lock = threading.Lock()
        self.next_id = 0
        self.pending = {}
        self.pending_lock = threading.Lock()

    def read_message(self):
        """Read one message; returns None at EOF."""
        headers = {}
        while True:
            line = self.reader.readline()
            if not line:
                return None
            line = line.decode("ascii", "replace").strip()
            if not line:
                if headers:
                    break
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        length = int(headers.get("content-length", 0))
        body = b""
        while len(body) < length:
            chunk = self.reader.read(length - len(body))
            if not chunk:
                return None
            body += chunk
        return json.loads(body.decode("utf-8"))

    def write_message(self, message):
        body = json.dumps(message, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        header = "Content-Length: {n}\r\n\r\n".format(n=len(body)).encode("ascii")
        with self.write_lock:
            self.writer.write(header + body)
            self.writer.flush()

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self.write_message(msg)

    def request(self, method, params=None, callback=None):
        """Send a request to the client; callback(result, error) is called with the response."""
        with self.pending_lock:
            self.next_id += 1
            msg_id = "coconut-" + str(self.next_id)
            self.pending[msg_id] = callback
        msg = {"jsonrpc": "2.0", "id": msg_id, "method": method}
        if params is not None:
            msg["params"] = params
        self.write_message(msg)

    def respond(self, msg_id, result=None, error=None):
        msg = {"jsonrpc": "2.0", "id": msg_id}
        if error is not None:
            msg["error"] = error
        else:
            msg["result"] = result
        self.write_message(msg)

    def handle_response(self, message):
        with self.pending_lock:
            callback = self.pending.pop(message.get("id"), None)
        if callback is not None:
            try:
                callback(message.get("result"), message.get("error"))
            except Exception:
                log(traceback.format_exc())


def stdio_connection():
    """Create a connection on the process's real stdin/stdout, and redirect sys.stdout to stderr
    so that stray prints (e.g. from the Coconut compiler) can't corrupt the protocol stream."""
    reader = sys.stdin.buffer
    writer = sys.stdout.buffer
    sys.stdout = sys.stderr
    return JsonRpcConnection(reader, writer)
