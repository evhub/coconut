#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: The Coconut language server.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import re
import sys
import threading
import time
import traceback

from coconut.lsp import docs
from coconut.lsp.compiler import DEFAULT_SETTINGS, SEVERITY_ERROR, first_error_line, make_range, repair_source
from coconut.lsp.intel import Analyzer, jedi_available
from coconut.lsp.protocol import (
    INVALID_PARAMS,
    METHOD_NOT_FOUND,
    REQUEST_FAILED,
    SERVER_NOT_INITIALIZED,
    LOG_FILE,
    ResponseError,
    log,
    stdio_connection,
)
from coconut.lsp.sourcemap import CompiledDocument, word_at
from coconut.lsp.symbols import WorkspaceIndex, document_symbols, flatten_symbols
from coconut.lsp.overlay import Overlay
from coconut.lsp.uris import path_to_uri, uri_to_path
from coconut.lsp.worker import CompileTimeout, WorkerClient

TEXT_SYNC_FULL = 1
ASTRAL_RE = re.compile(u"[\U00010000-\U0010FFFF]")
CHANGE_DEBOUNCE = 0.35
MAX_REPAIRS = 3
FIRST_COMPILE_WAIT = 5.0
REPAIR_TIME_BUDGET = 4.0
MESSAGE_ERROR = 1
MESSAGE_WARNING = 2
MESSAGE_INFO = 3


def flatten_settings(settings):
    """Accept {coconut: {target, strict, languageServer: {lint}}} or already-flat dicts."""
    if not isinstance(settings, dict):
        return {}
    if isinstance(settings.get("coconut"), dict):
        settings = settings["coconut"]
    flat = {}
    for key, value in settings.items():
        if key == "languageServer" and isinstance(value, dict):
            flat.update(flatten_settings(value))
        else:
            flat[key] = value
    return flat


class Document(object):

    def __init__(self, uri, path, text, version):
        self.uri = uri
        self.path = path
        self.text = text
        self.version = version
        self.good = None  # last successful CompiledDocument
        self.good_version = None
        self.compiled_version = None  # version of the last compile attempt
        self.diagnostics = []
        self.needs_compile = True
        self.compile_after = 0.0
        self.compiled_event = threading.Event()
        self.mypy_diagnostics = []
        self.mypy_source = None  # the text mypy_diagnostics were computed for


class CoconutLanguageServer(object):

    def __init__(self, conn, compiler=None, default_settings=None):
        self.conn = conn
        self.compiler = compiler or WorkerClient()
        self.docs = {}
        self.cond = threading.Condition()
        self.settings = dict(DEFAULT_SETTINGS)
        if default_settings:
            self.settings.update(default_settings)
        self.roots = []
        self.initialized = False
        self.shutting_down = False
        self.exit_code = None
        self.index = WorkspaceIndex()
        self.overlay = Overlay(self.compile_for_overlay)
        self.info = None
        self.reported_fatal = False
        self.compile_thread = threading.Thread(target=self.compile_loop, name="coconut-compile")
        self.compile_thread.daemon = True
        self.mypy_queue = []
        self.mypy_cond = threading.Condition()
        self.mypy_thread = threading.Thread(target=self.mypy_loop, name="coconut-mypy")
        self.mypy_thread.daemon = True
        self.reported_no_mypy = False
        self.utf32 = False  # whether the client accepted UTF-32 (code point) positions
        self.initialized_event = threading.Event()
        self.handlers = {
            "initialize": self.on_initialize,
            "initialized": self.on_initialized,
            "shutdown": self.on_shutdown,
            "exit": self.on_exit,
            "$/cancelRequest": lambda params: None,
            "$/setTrace": lambda params: None,
            "workspace/didChangeConfiguration": self.on_did_change_configuration,
            "workspace/didChangeWorkspaceFolders": self.on_did_change_workspace_folders,
            "workspace/didChangeWatchedFiles": lambda params: None,
            "workspace/symbol": self.on_workspace_symbol,
            "textDocument/didOpen": self.on_did_open,
            "textDocument/didChange": self.on_did_change,
            "textDocument/didSave": self.on_did_save,
            "textDocument/didClose": self.on_did_close,
            "textDocument/hover": self.on_hover,
            "textDocument/completion": self.on_completion,
            "textDocument/signatureHelp": self.on_signature_help,
            "textDocument/definition": self.on_definition,
            "textDocument/declaration": self.on_definition,
            "textDocument/typeDefinition": self.on_type_definition,
            "textDocument/references": self.on_references,
            "textDocument/documentHighlight": self.on_document_highlight,
            "textDocument/documentSymbol": self.on_document_symbol,
            "textDocument/prepareRename": self.on_prepare_rename,
            "textDocument/rename": self.on_rename,
            "textDocument/codeAction": self.on_code_action,
            "coconut/compiled": self.on_compiled,
            "coconut/info": self.on_info,
        }

    # ------------------------------------------------------------------ main loop

    def run(self):
        self.compile_thread.start()
        self.mypy_thread.start()
        while self.exit_code is None:
            try:
                message = self.conn.read_message()
            except Exception:
                log("failed to read message:", traceback.format_exc())
                continue
            if message is None:
                break
            self.dispatch(message)
        from coconut.lsp.typecheck import kill_running
        kill_running()
        self.compiler.close()
        return self.exit_code if self.exit_code is not None else (0 if self.shutting_down else 1)

    def dispatch(self, message):
        if LOG_FILE:
            log("<-", message.get("method", "response"), message.get("id", ""))
        if "method" not in message:
            self.conn.handle_response(message)
            return
        method = message["method"]
        msg_id = message.get("id")
        params = message.get("params") or {}
        handler = self.handlers.get(method)
        is_request = "id" in message
        if handler is None:
            if is_request:
                self.conn.respond(msg_id, error={"code": METHOD_NOT_FOUND, "message": "unknown method " + method})
            return
        if is_request and not self.initialized and method not in ("initialize", "shutdown"):
            self.conn.respond(msg_id, error={"code": SERVER_NOT_INITIALIZED, "message": "server not initialized"})
            return
        try:
            result = handler(params)
            if is_request:
                if result is not None and not method.startswith(("initialize", "coconut/")):
                    uri = (params.get("textDocument") or {}).get("uri")
                    result = self.encode_positions(result, uri)
                self.conn.respond(msg_id, result)
        except ResponseError as err:
            if is_request:
                self.conn.respond(msg_id, error={"code": err.code, "message": err.message})
        except Exception as err:
            log("error handling {m}:".format(m=method), traceback.format_exc())
            if is_request:
                self.conn.respond(msg_id, error={"code": REQUEST_FAILED, "message": "{t}: {e}".format(t=type(err).__name__, e=err)})

    # ------------------------------------------------------------------ lifecycle

    def on_initialize(self, params):
        self.initialized = True
        roots = []
        for folder in params.get("workspaceFolders") or []:
            path = uri_to_path(folder.get("uri", ""))
            if path:
                roots.append(path)
        if not roots:
            if params.get("rootUri"):
                roots.append(uri_to_path(params["rootUri"]))
            elif params.get("rootPath"):
                roots.append(params["rootPath"])
        self.roots = [r for r in roots if r]
        self.update_settings(params.get("initializationOptions"))
        encodings = ((params.get("capabilities") or {}).get("general") or {}).get("positionEncodings") or []
        self.utf32 = "utf-32" in encodings
        return {
            "capabilities": {
                "positionEncoding": "utf-32" if self.utf32 else "utf-16",
                "textDocumentSync": {"openClose": True, "change": TEXT_SYNC_FULL, "save": {"includeText": False}},
                "hoverProvider": True,
                "completionProvider": {"triggerCharacters": ["."], "resolveProvider": False},
                "signatureHelpProvider": {"triggerCharacters": ["(", ","], "retriggerCharacters": [","]},
                "definitionProvider": True,
                "declarationProvider": True,
                "typeDefinitionProvider": True,
                "referencesProvider": True,
                "documentHighlightProvider": True,
                "documentSymbolProvider": True,
                "workspaceSymbolProvider": True,
                "renameProvider": {"prepareProvider": True},
                "codeActionProvider": {"codeActionKinds": ["quickfix"]},
                "workspace": {"workspaceFolders": {"supported": True, "changeNotifications": True}},
            },
            "serverInfo": {"name": "coconut-lsp", "version": VERSION_STR},
        }

    def on_initialized(self, params):
        self.initialized_event.set()
        with self.cond:
            self.cond.notify_all()

    def on_shutdown(self, params):
        self.shutting_down = True
        with self.cond:
            self.cond.notify_all()
        with self.mypy_cond:
            self.mypy_cond.notify_all()
        return None

    def on_exit(self, params):
        self.exit_code = 0 if self.shutting_down else 1

    def update_settings(self, raw):
        flat = flatten_settings(raw)
        new = dict(self.settings)
        for key in DEFAULT_SETTINGS:
            if key in flat and flat[key] is not None and flat[key] != "":
                new[key] = flat[key]
        if "compileTimeout" in flat:
            try:
                self.compiler.timeout = float(flat["compileTimeout"])
            except (TypeError, ValueError):
                pass
        changed = new != self.settings
        self.settings = new
        return changed

    def on_did_change_configuration(self, params):
        if self.update_settings(params.get("settings")):
            with self.cond:
                docs = list(self.docs.values())
                for doc in docs:
                    doc.needs_compile = True
                    doc.compile_after = 0
                    if not self.settings.get("mypy"):
                        doc.mypy_diagnostics = []
                self.cond.notify_all()
            for doc in docs:
                self.request_mypy(doc)

    def on_did_change_workspace_folders(self, params):
        event = params.get("event") or {}
        removed = set(uri_to_path(f["uri"]) for f in event.get("removed", []))
        self.roots = [r for r in self.roots if r not in removed]
        for f in event.get("added", []):
            self.roots.append(uri_to_path(f["uri"]))

    # ------------------------------------------------------------------ document sync

    def doc_path(self, uri):
        path = uri_to_path(uri)
        if path:
            return path
        base = self.roots[0] if self.roots else os.getcwd()
        name = re.sub(r"\W+", "_", uri.split(":", 1)[-1]) or "untitled"
        return os.path.join(base, name + ".coco")

    def schedule(self, doc, delay):
        doc.needs_compile = True
        doc.compile_after = time.time() + delay
        doc.compiled_event.clear()
        self.cond.notify_all()

    def on_did_open(self, params):
        td = params["textDocument"]
        with self.cond:
            doc = Document(td["uri"], self.doc_path(td["uri"]), td.get("text", ""), td.get("version"))
            self.docs[td["uri"]] = doc
            self.schedule(doc, 0)
        self.request_mypy(doc)

    def on_did_change(self, params):
        td = params["textDocument"]
        with self.cond:
            doc = self.docs.get(td["uri"])
            if doc is None:
                return
            for change in params.get("contentChanges", []):
                if "range" in change:
                    doc.text = apply_edit(doc.text, change["range"], change["text"])
                else:
                    doc.text = change["text"]
            doc.version = td.get("version")
            self.schedule(doc, CHANGE_DEBOUNCE)

    def on_did_save(self, params):
        with self.cond:
            doc = self.docs.get(params["textDocument"]["uri"])
            if doc is not None and doc.compiled_version != doc.version:
                self.schedule(doc, 0)
        if doc is not None:
            self.request_mypy(doc)

    def on_did_close(self, params):
        uri = params["textDocument"]["uri"]
        with self.cond:
            doc = self.docs.pop(uri, None)
            if doc is not None:
                doc.compiled_event.set()  # unblock anything waiting on this document
            self.conn.notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": []})

    # ------------------------------------------------------------------ compilation

    def compile_loop(self):
        try:
            self.info = self.compiler.call("info", timeout=60)
        except Exception as err:
            self.info = {"coconut_version": None, "coconut_error": str(err), "python_executable": sys.executable}
        # clients may only listen for notifications once initialization is complete
        self.initialized_event.wait(30)
        self.send_status()
        if self.info.get("coconut_version"):
            try:
                self.compiler.call("warm_up", {"settings": self.settings}, timeout=120)
            except Exception:
                log("warm up failed:", traceback.format_exc())
        while True:
            with self.cond:
                if self.shutting_down or self.exit_code is not None:
                    return
                now = time.time()
                due = None
                wait = None
                for doc in self.docs.values():
                    if doc.needs_compile:
                        remaining = doc.compile_after - now
                        if remaining <= 0:
                            due = doc
                            break
                        wait = remaining if wait is None else min(wait, remaining)
                if due is None:
                    self.cond.wait(wait if wait is not None else 1.0)
                    continue
                doc = due
                text, version = doc.text, doc.version
                doc.needs_compile = False
                settings = dict(self.settings)
            self.compile_document(doc, text, version, settings)

    def compile_document(self, doc, text, version, settings):
        started = time.time()
        try:
            result = self.compiler.call("compile", {"code": text, "settings": settings})
        except CompileTimeout as err:
            result = {"compiled": None, "diagnostics": [{
                "range": make_range(0, 0, 0, 0), "severity": SEVERITY_ERROR, "source": "coconut",
                "message": "Coconut " + str(err) + " (see the coconut.languageServer.compileTimeout setting)",
            }]}
        except Exception as err:
            log("compile failed:", err)
            result = {"compiled": None, "diagnostics": []}
        good_text, good_compiled = text, result.get("compiled")
        slow = time.time() - started > REPAIR_TIME_BUDGET / 2
        if good_compiled is None and not result.get("fatal") and not (slow and doc.good is not None):
            good_text, good_compiled = self.repaired_compile(text, result.get("diagnostics", []), settings)
        if result.get("fatal"):
            if not self.reported_fatal:
                self.reported_fatal = True
                self.conn.notify("window/showMessage", {"type": MESSAGE_WARNING, "message": result["fatal"]})
            self.send_status()
        with self.cond:
            if self.docs.get(doc.uri) is not doc:
                return
            if good_compiled is not None:
                try:
                    doc.good = CompiledDocument(good_text, good_compiled)
                    doc.good_version = version if good_text is text else None
                except Exception:
                    log("failed to process compiled code:", traceback.format_exc())
            doc.compiled_version = version
            current = doc.version == version
            if current:
                doc.diagnostics = result.get("diagnostics", [])
                doc.compiled_event.set()
        if current:
            self.publish(doc)
            self.conn.notify("coconut/compiled", {"uri": doc.uri, "version": version, "success": result.get("compiled") is not None})
        if jedi_available() and good_compiled is not None:
            try:
                self.overlay.prepare(doc.path, text, self.roots)
            except Exception:
                log("failed to prepare imports:", traceback.format_exc())

    def publish(self, doc):
        """Publish the compiler/lint diagnostics plus any (line-adjusted) mypy diagnostics."""
        with self.cond:
            diagnostics = list(doc.diagnostics)
            version = doc.version
            if doc.mypy_diagnostics and doc.mypy_source is not None:
                from coconut.lsp.sourcemap import LineDiff
                diff = LineDiff(doc.mypy_source.splitlines(), doc.text.splitlines())
                for diag in doc.mypy_diagnostics:
                    line = diff.old_to_new(diag["range"]["start"]["line"])
                    if line is None:
                        continue
                    moved = dict(diag)
                    moved["range"] = make_range(line, diag["range"]["start"]["character"], line, diag["range"]["end"]["character"])
                    diagnostics.append(moved)
            # send while holding the lock, so that diagnostics can't arrive out of order or after didClose
            if self.docs.get(doc.uri) is not doc:
                return
            import copy
            diagnostics = self.encode_positions(copy.deepcopy(diagnostics), doc.uri)
            self.conn.notify("textDocument/publishDiagnostics", {"uri": doc.uri, "version": version, "diagnostics": diagnostics})

    # ------------------------------------------------------------------ mypy

    def request_mypy(self, doc):
        if not self.settings.get("mypy"):
            return
        with self.mypy_cond:
            if doc.uri not in self.mypy_queue:
                self.mypy_queue.append(doc.uri)
            self.mypy_cond.notify_all()

    def mypy_loop(self):
        from coconut.lsp.typecheck import mypy_available, run_mypy
        while True:
            with self.mypy_cond:
                while not self.mypy_queue and not self.shutting_down:
                    self.mypy_cond.wait(1.0)
                if self.shutting_down:
                    return
                uri = self.mypy_queue.pop(0)
            doc = self.docs.get(uri)
            if doc is None or not self.settings.get("mypy"):
                continue
            if not mypy_available():
                if not self.reported_no_mypy:
                    self.reported_no_mypy = True
                    self.conn.notify("window/showMessage", {
                        "type": MESSAGE_WARNING,
                        "message": "Coconut: type checking is enabled but mypy isn't installed for {exe} (install it with: {exe} -m pip install mypy)".format(exe=sys.executable),
                    })
                continue
            # type-check the version that was just saved/opened, once it has compiled
            doc.compiled_event.wait(self.compiler.timeout)
            with self.cond:
                if self.docs.get(uri) is not doc or doc.good is None or doc.good_version != doc.version:
                    log("skipping mypy for", uri, "(closed, changed, or doesn't compile)")
                    continue
                source, compiled = doc.good.source, doc.good.compiled
            try:
                diagnostics = run_mypy(doc.path, source, compiled, self.overlay, self.roots)
            except Exception:
                log("mypy failed:", traceback.format_exc())
                continue
            with self.cond:
                if self.docs.get(uri) is not doc:
                    continue
                doc.mypy_diagnostics = diagnostics
                doc.mypy_source = source
            self.publish(doc)

    def compile_for_overlay(self, text):
        result = self.compiler.call("compile", {"code": text, "settings": dict(self.settings, lint=False)})
        return result.get("compiled")

    def repaired_compile(self, text, diagnostics, settings):
        """After a failed compile, compile a version with the broken line(s) neutralized, so
        that hover/completion/etc. keep working for the rest of the file."""
        start = time.time()
        settings = dict(settings, lint=False)
        for _ in range(MAX_REPAIRS):
            line = first_error_line(diagnostics)
            if line is None or time.time() - start > REPAIR_TIME_BUDGET:
                break
            repaired = repair_source(text, line)
            if repaired is None:
                break
            try:
                result = self.compiler.call("compile", {"code": repaired, "settings": settings})
            except Exception:
                break
            text, diagnostics = repaired, result.get("diagnostics", [])
            if result.get("compiled") is not None:
                return text, result["compiled"]
        return None, None

    def send_status(self):
        info = dict(self.info or {})
        info["jedi"] = jedi_available()
        info["server_version"] = VERSION_STR
        self.conn.notify("coconut/status", info)

    # ------------------------------------------------------------------ helpers

    def get_doc(self, params):
        uri = params["textDocument"]["uri"]
        doc = self.docs.get(uri)
        if doc is None:
            raise ResponseError(INVALID_PARAMS, "document not open: " + uri)
        return doc

    def analyzer(self, doc):
        if doc.good is None and doc.compiled_version is None:
            # the document's first compile is still running; give it a moment
            doc.compiled_event.wait(FIRST_COMPILE_WAIT)
        with self.cond:
            text, good = doc.text, doc.good
        return Analyzer(doc.path, text, good, self.roots, self.overlay)

    def position(self, params):
        """The request's position as (line, code point index)."""
        pos = params["position"]
        line, char = pos["line"], pos["character"]
        if not self.utf32:
            doc = self.docs.get((params.get("textDocument") or {}).get("uri"))
            if doc is not None:
                lines = doc.text.split("\n")
                if 0 <= line < len(lines) and ASTRAL_RE.search(lines[line]):
                    char = utf16_to_index(lines[line], char)
        return line, char

    def _lines_for(self, uri, cache):
        if uri not in cache:
            doc = self.docs.get(uri)
            if doc is not None:
                text = doc.text
            else:
                path = uri_to_path(uri) if uri else None
                try:
                    with open(path, encoding="utf-8") as f:
                        text = f.read()
                except (OSError, TypeError, UnicodeDecodeError, ValueError):
                    text = ""
            cache[uri] = text.split("\n") if ASTRAL_RE.search(text) else None
        return cache[uri]

    def encode_positions(self, obj, uri, cache=None):
        """Convert the code point columns in a result to UTF-16 (LSP's default), in place.

        Positions are converted relative to the document named by the nearest enclosing 'uri'
        (or the request's document). 'diagnostics' echoed back from the client are skipped."""
        if self.utf32:
            return obj
        cache = {} if cache is None else cache
        if isinstance(obj, list):
            for item in obj:
                self.encode_positions(item, uri, cache)
        elif isinstance(obj, dict):
            if set(obj) == {"line", "character"}:
                lines = self._lines_for(uri, cache)
                if lines is not None and 0 <= obj["line"] < len(lines):
                    text = lines[obj["line"]]
                    obj["character"] += len(ASTRAL_RE.findall(text[:obj["character"]]))
                return obj
            own_uri = obj.get("uri", obj.get("targetUri"))
            if isinstance(own_uri, str):
                uri = own_uri
            for key, value in obj.items():
                if key == "diagnostics":
                    continue
                if key == "changes" and isinstance(value, dict):
                    for edit_uri, edits in value.items():
                        self.encode_positions(edits, edit_uri, cache)
                elif isinstance(value, (dict, list)):
                    self.encode_positions(value, uri, cache)
        return obj

    def location(self, loc):
        path, line, start, end = loc
        return {"uri": path_to_uri(path), "range": make_range(line, start, line, end)}

    def doc_uri_for_path(self, path, default_doc):
        if path == default_doc.path:
            return default_doc.uri
        return path_to_uri(path)

    # ------------------------------------------------------------------ language features

    def on_hover(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        result = self.analyzer(doc).hover(line, col)
        if result is None:
            return None
        markdown, (l, s, e) = result
        return {"contents": {"kind": "markdown", "value": markdown}, "range": make_range(l, s, l, e)}

    def on_completion(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        items = self.analyzer(doc).completions(line, col)
        return {"isIncomplete": False, "items": items}

    def on_signature_help(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        return self.analyzer(doc).signature_help(line, col)

    def locations_for(self, doc, locs):
        result = []
        for path, line, start, end in locs:
            result.append({"uri": self.doc_uri_for_path(path, doc), "range": make_range(line, start, line, end)})
        return result

    def on_definition(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        return self.locations_for(doc, self.analyzer(doc).definitions(line, col))

    def on_type_definition(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        analyzer = self.analyzer(doc)
        at = analyzer._jedi_at(line, col)
        if at is None:
            return []
        script, jl, jc, inserted_at = at
        try:
            names = script.infer(jl, jc)
        except Exception:
            return []
        locs = []
        for n in names:
            loc = analyzer.name_to_location(n, inserted_at)
            if loc is not None and loc not in locs:
                locs.append(loc)
        return self.locations_for(doc, locs)

    def on_references(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        include_decl = (params.get("context") or {}).get("includeDeclaration", True)
        return self.locations_for(doc, self.analyzer(doc).references(line, col, include_decl))

    def on_document_highlight(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        refs = self.analyzer(doc).references(line, col)
        return [{"range": make_range(l, s, l, e), "kind": 1} for path, l, s, e in refs if path == doc.path]

    def current_symbols(self, doc):
        with self.cond:
            text, good = doc.text, doc.good
        if good is None:
            return []
        analyzer = Analyzer(doc.path, text, good, self.roots)
        return document_symbols(good, analyzer.diff.old_to_new)

    def on_document_symbol(self, params):
        doc = self.get_doc(params)
        if doc.good is None and doc.compiled_version is None:
            doc.compiled_event.wait(FIRST_COMPILE_WAIT)
        symbols = self.current_symbols(doc)
        if not symbols:
            # fall back to a quick regex scan (e.g. the file has never compiled), nested by indentation
            from coconut.lsp.symbols import scan_symbols
            lines = doc.text.splitlines()
            stack = []  # (indent, symbol)
            for name, kind, line, col, indent in scan_symbols(doc.text):
                rng = make_range(line, col, line, len(lines[line]) if line < len(lines) else col)
                sym = {"name": name, "kind": kind, "range": rng,
                       "selectionRange": make_range(line, col, line, col + len(name)), "children": []}
                while stack and stack[-1][0] >= indent:
                    stack.pop()
                if stack:
                    stack[-1][1]["children"].append(sym)
                else:
                    symbols.append(sym)
                if kind != 13 and kind != 14:  # variables can't contain anything
                    stack.append((indent, sym))
        return symbols

    def on_workspace_symbol(self, params):
        query = params.get("query", "")
        open_docs = {}
        for doc in list(self.docs.values()):
            syms = []
            for sym, container in flatten_symbols(self.current_symbols(doc)):
                start = sym["selectionRange"]["start"]
                syms.append((sym["name"], sym["kind"], start["line"], start["character"], container))
            if syms:
                open_docs[doc.path] = syms
        results = []
        for name, kind, path, line, col, container in self.index.search(self.roots, query, open_docs):
            info = {
                "name": name,
                "kind": kind,
                "location": {"uri": path_to_uri(path), "range": make_range(line, col, line, col + len(name))},
            }
            if container:
                info["containerName"] = container
            results.append(info)
        return results

    def check_rename_safe(self, doc):
        with self.cond:
            safe = doc.good is not None and doc.good_version == doc.version and doc.good.source == doc.text
        if not safe:
            raise ResponseError(REQUEST_FAILED, "Coconut: can't rename until the file compiles without errors (fix them and try again in a moment)")

    def on_prepare_rename(self, params):
        doc = self.get_doc(params)
        self.check_rename_safe(doc)
        line, col = self.position(params)
        analyzer = self.analyzer(doc)
        found = word_at(analyzer.line(line), col)
        if found is None or docs.is_keyword(found[0]):
            return None
        try:
            name, refs = analyzer.rename_locations(line, col)
        except ValueError as err:
            raise ResponseError(REQUEST_FAILED, str(err))
        return {"range": make_range(line, found[1], line, found[2]), "placeholder": name}

    def on_rename(self, params):
        doc = self.get_doc(params)
        line, col = self.position(params)
        self.check_rename_safe(doc)
        new_name = params.get("newName", "")
        if not re.match(r"^[A-Za-z_]\w*$", new_name):
            raise ResponseError(REQUEST_FAILED, "invalid identifier: " + repr(new_name))
        try:
            name, refs = self.analyzer(doc).rename_locations(line, col)
        except ValueError as err:
            raise ResponseError(REQUEST_FAILED, str(err))
        edits = [{"range": make_range(l, s, l, e), "newText": new_name} for path, l, s, e in refs]
        return {"changes": {doc.uri: edits}}

    def on_code_action(self, params):
        doc = self.get_doc(params)
        lines = doc.text.splitlines()
        actions = []
        for diag in (params.get("context") or {}).get("diagnostics", []):
            line = diag["range"]["start"]["line"]
            text = lines[line] if 0 <= line < len(lines) else ""
            message = diag.get("message", "")
            unused = re.search(r"(?:unused import '([\w.]+)'|'([\w.]+)' imported but unused)", message)
            if unused:
                action = remove_import_action(doc.uri, lines, line, (unused.group(1) or unused.group(2)), diag)
                if action is not None:
                    actions.append(action)
            if (diag.get("data") or {}).get("noqa") or "NOQA" in message:
                if "NOQA" not in text:
                    end = len(text)
                    actions.append({
                        "title": "Suppress with # NOQA",
                        "kind": "quickfix",
                        "diagnostics": [diag],
                        "edit": {"changes": {doc.uri: [{"range": make_range(line, end, line, end), "newText": "  # NOQA"}]}},
                    })
        return actions

    # ------------------------------------------------------------------ custom requests

    def on_compiled(self, params):
        """Return the compiled Python for a document (waiting briefly for an in-progress compile)."""
        doc = self.get_doc(params)
        timeout = min(float(params.get("timeout", 2)), 10)
        with self.cond:
            if doc.compiled_version != doc.version:
                doc.compile_after = min(doc.compile_after, time.time())
                self.cond.notify_all()
        doc.compiled_event.wait(timeout)
        with self.cond:
            errors = [d for d in doc.diagnostics if d.get("severity") == SEVERITY_ERROR]
            return {
                "compiled": doc.good.compiled if doc.good is not None else None,
                "upToDate": doc.good is not None and doc.good_version == doc.version,
                "errors": errors,
                "version": doc.good_version,
            }

    def on_info(self, params):
        info = dict(self.info or {})
        info["jedi"] = jedi_available()
        info["server_version"] = VERSION_STR
        info["settings"] = self.settings
        return info


def apply_edit(text, rng, new_text):
    """Apply an LSP range edit (used if a client sends incremental changes anyway)."""
    lines = text.split("\n")

    def offset(pos):
        line = min(pos["line"], len(lines))
        off = sum(len(ln) + 1 for ln in lines[:line])
        if line < len(lines):
            off += utf16_to_index(lines[line], pos["character"])
        return min(off, len(text))

    start, end = offset(rng["start"]), offset(rng["end"])
    return text[:start] + new_text + text[end:]


def utf16_to_index(line, char):
    idx = 0
    units = 0
    for ch in line:
        if units >= char:
            break
        units += 2 if ord(ch) > 0xFFFF else 1
        idx += 1
    return idx


def remove_import_action(uri, lines, line, name, diag):
    text = lines[line] if 0 <= line < len(lines) else ""
    short = name.split(".")[-1]
    single = re.match(r"^\s*(?:import\s+[\w.]+(?:\s+as\s+\w+)?|from\s+[\w.]+\s+import\s+\w+(?:\s+as\s+\w+)?)\s*(?:#.*)?$", text)
    if single:
        edit = {"range": make_range(line, 0, line + 1, 0), "newText": ""}
    else:
        m = re.match(r"^(\s*from\s+[\w.]+\s+import\s+)(.+?)(\s*(?:#.*)?)$", text)
        if not m or "(" in m.group(2):
            return None
        parts = [p.strip() for p in m.group(2).split(",")]
        kept = [p for p in parts if p.split(" as ")[-1].strip() != short]
        if len(kept) == len(parts) or not kept:
            return None
        edit = {"range": make_range(line, 0, line, len(text)), "newText": m.group(1) + ", ".join(kept) + m.group(3)}
    return {
        "title": "Remove unused import '{n}'".format(n=short),
        "kind": "quickfix",
        "diagnostics": [diag],
        "isPreferred": True,
        "edit": {"changes": {uri: [edit]}},
    }


def serve_stdio(default_settings=None):
    conn = stdio_connection()
    server = CoconutLanguageServer(conn, default_settings=default_settings)
    return server.run()


def main(args=None, default_settings=None):
    """Start the Coconut language server over stdio (the entry point for 'coconut --lsp').

    default_settings (e.g. from 'coconut --lsp --strict --pure --target 3.10') are used unless
    the client overrides them with its initialization options or configuration."""
    return serve_stdio(default_settings)
