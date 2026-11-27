#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: A Model Context Protocol (MCP) server exposing Coconut tooling to AI agents.

Run with:  coconut --mcp  (or: python -m coconut.lsp mcp)

Tools: check Coconut code for errors, compile it to Python, look up Coconut documentation, and
query code intelligence (hover, definition, references, symbols). Speaks MCP's stdio transport
(newline-delimited JSON-RPC 2.0) with no dependencies beyond Coconut itself.

Don't rename this module: the VS Code and Sublime Text packages (evhub/sublime-coconut) check
whether coconut.lsp.mcp is importable to decide whether the installed Coconut has this language
server, and use their own bundled copy of it otherwise.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import json
import os
import sys
import traceback

from coconut.lsp import docs

PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")

POSITION_PROPS = {
    "path": {"type": "string", "description": "Path to a Coconut (.coco) file"},
    "line": {"type": "integer", "minimum": 1, "description": "1-based line number"},
    "column": {"type": "integer", "minimum": 1, "description": "1-based column number"},
}

SOURCE_PROPS = {
    "path": {"type": "string", "description": "Path to a Coconut file (or, for coconut_check, a directory)"},
    "code": {"type": "string", "description": "Coconut source code (instead of path)"},
    "target": {"type": "string", "description": "Python version to target, e.g. 'sys' (default), '3.8', '2.7'"},
}

TOOLS = [
    {
        "name": "coconut_check",
        "description": (
            "Compile Coconut code and report errors and warnings (syntax errors, undefined names, unused "
            "imports/variables, ...) with 1-based line/column positions. Pass a file or directory 'path', or "
            "'code'. Use this after editing Coconut files to verify they compile."
        ),
        "inputSchema": {"type": "object", "properties": dict(
            SOURCE_PROPS,
            strict={"type": "boolean", "description": "Enable Coconut's --strict style checks"},
            mypy={"type": "boolean", "description": "Also type-check the compiled code with mypy (must be installed)"},
        ), "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "coconut_compile",
        "description": (
            "Compile Coconut code to Python and return the Python. Useful for understanding exactly what a "
            "piece of Coconut syntax does. Pass 'path' or 'code'."
        ),
        "inputSchema": {"type": "object", "properties": dict(SOURCE_PROPS, include_header={
            "type": "boolean", "description": "Include Coconut's import header (default false)"}), "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "coconut_docs",
        "description": (
            "Look up Coconut's documentation for a built-in function (e.g. 'fmap', 'reduce', 'addpattern'), "
            "keyword (e.g. 'match', 'case', 'data', 'where'), or operator (e.g. '|>', '..', '$', '??', '=>'). "
            "Also accepts free-text queries like 'pattern matching' or 'partial application'. Omit 'query' to "
            "list everything documented."
        ),
        "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "coconut_hover",
        "description": "Get the type, signature, and documentation of the symbol at a position in a Coconut file.",
        "inputSchema": {"type": "object", "properties": POSITION_PROPS, "required": ["path", "line", "column"], "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "coconut_definition",
        "description": "Find where the symbol at a position in a Coconut file is defined.",
        "inputSchema": {"type": "object", "properties": POSITION_PROPS, "required": ["path", "line", "column"], "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "coconut_references",
        "description": "Find all references (within the same file) to the symbol at a position in a Coconut file.",
        "inputSchema": {"type": "object", "properties": POSITION_PROPS, "required": ["path", "line", "column"], "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "coconut_symbols",
        "description": "List the classes, data types, functions, and variables defined in a Coconut file, with positions.",
        "inputSchema": {"type": "object", "properties": {"path": POSITION_PROPS["path"]}, "required": ["path"], "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
]


def _display_path(path):
    """A path relative to the current directory when that's shorter (relpath fails across Windows drives)."""
    try:
        rel = os.path.relpath(path)
    except ValueError:
        return path
    return rel if len(rel) < len(path) else path


class ToolError(Exception):
    pass


class McpServer(object):

    def __init__(self, reader=None, writer=None):
        self.reader = reader or sys.stdin
        self.writer = writer or sys.stdout
        self.engines = {}

    def engine(self, target=None, strict=False, mypy=False):
        from coconut.lsp.cli import Engine
        key = (target or "", bool(strict), bool(mypy))
        if key not in self.engines:
            settings = {}
            if target:
                settings["target"] = target
            if strict:
                settings["strict"] = True
            if mypy:
                settings["mypy"] = True
            self.engines[key] = Engine(settings)
        return self.engines[key]

    def send(self, message):
        self.writer.write(json.dumps(message) + "\n")
        self.writer.flush()

    def run(self):
        for line in self.reader:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except ValueError:
                self.send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
                continue
            for msg in (message if isinstance(message, list) else [message]):
                response = self.handle(msg)
                if response is not None:
                    self.send(response)
        return 0

    def handle(self, msg):
        method = msg.get("method")
        msg_id = msg.get("id")
        if method is None:
            return None  # a response to something we never send
        params = msg.get("params") or {}
        try:
            if method == "initialize":
                requested = params.get("protocolVersion")
                result = {
                    "protocolVersion": requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "coconut", "title": "Coconut", "version": VERSION_STR},
                    "instructions": (
                        "Tools for the Coconut programming language (a functional superset of Python that compiles "
                        "to Python; files end in .coco). Use coconut_check after editing .coco files, coconut_docs "
                        "to look up unfamiliar Coconut syntax or built-ins, and coconut_compile to see the Python a "
                        "construct compiles to. Lines and columns are 1-based."
                    ),
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                result = self.call_tool(params.get("name"), params.get("arguments") or {})
            elif method.startswith("notifications/"):
                return None
            else:
                if msg_id is None:
                    return None
                return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "unknown method " + str(method)}}
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            if msg_id is None:
                return None
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(err)}}
        if msg_id is None:
            return None
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def call_tool(self, name, args):
        handler = getattr(self, "tool_" + str(name).replace("coconut_", "", 1), None)
        if handler is None or not str(name).startswith("coconut_"):
            return {"content": [{"type": "text", "text": "unknown tool: " + str(name)}], "isError": True}
        try:
            text = handler(args)
            return {"content": [{"type": "text", "text": text}], "isError": False}
        except ToolError as err:
            return {"content": [{"type": "text", "text": str(err)}], "isError": True}
        except (OSError, UnicodeDecodeError, RuntimeError) as err:
            return {"content": [{"type": "text", "text": "{t}: {e}".format(t=type(err).__name__, e=err)}], "isError": True}

    # ------------------------------------------------------------------ tools

    @staticmethod
    def _source(args):
        path, code = args.get("path"), args.get("code")
        if code is None and not path:
            raise ToolError("pass either 'path' or 'code'")
        if code is not None:
            return (os.path.abspath(path) if path else os.path.join(os.getcwd(), "<code>.coco")), code
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            raise ToolError("no such file: " + path)
        return path, None

    def tool_check(self, args):
        from coconut.lsp.cli import collect_files, diag_to_json
        engine = self.engine(args.get("target"), args.get("strict"), args.get("mypy"))
        path, code = self._source(args)
        files = [path] if code is not None else collect_files([path])
        lines = []
        errors = warnings = 0
        for f in files:
            for diag in sorted(engine.check(f, code), key=lambda d: (d["range"]["start"]["line"], d["range"]["start"]["character"])):
                d = diag_to_json(f, diag)
                if d["severity"] == "error":
                    errors += 1
                elif d["severity"] == "warning":
                    warnings += 1
                elif d["severity"] == "hint" and "unused" not in d["message"]:
                    continue
                shown = os.path.basename(f) if code is not None else _display_path(f)
                lines.append("{f}:{l}:{c}: {s}: {m}".format(f=shown, l=d["line"], c=d["column"], s=d["severity"], m=d["message"]))
        summary = "Checked {n} file{s}: {e} error{es}, {w} warning{ws}.".format(
            n=len(files), s="" if len(files) == 1 else "s", e=errors, es="" if errors == 1 else "s",
            w=warnings, ws="" if warnings == 1 else "s",
        )
        return "\n".join([summary] + lines)

    def tool_compile(self, args):
        from coconut.lsp.cli import format_diag
        from coconut.lsp.sourcemap import strip_line_comment
        engine = self.engine(args.get("target"))
        path, code = self._source(args)
        if code is None and os.path.isdir(path):
            raise ToolError("coconut_compile takes a file, not a directory")
        result, good = engine.compile(path, code)
        if result.get("fatal"):
            raise ToolError(result["fatal"])
        if result.get("compiled") is None:
            errors = [format_diag(os.path.basename(path), d) for d in result["diagnostics"] if d.get("severity") == 1]
            raise ToolError("doesn't compile:\n" + "\n".join(errors))
        lines = good.compiled_lines
        if not args.get("include_header"):
            lines = lines[good.body_start:]
        return "\n".join(strip_line_comment(ln) for ln in lines).strip("\n") + "\n"

    def tool_docs(self, args):
        query = (args.get("query") or "").strip()
        if not query:
            entries = docs.all_docs()
            by_title = {}
            for key, entry in sorted(entries.items()):
                by_title.setdefault((entry["category"], entry["title"]), []).append(key)
            out = ["Documented Coconut features (query any name in backticks):"]
            for (category, title), keys in sorted(by_title.items()):
                out.append("- [{c}] {t}: ".format(c=category, t=title) + ", ".join("`" + k + "`" for k in keys))
            return "\n".join(out)
        results = docs.search(query)
        if not results:
            raise ToolError("no Coconut documentation found for {q!r}; call coconut_docs with no query to list topics".format(q=query))
        return "\n\n========\n\n".join(docs.format_entry(entry) for key, entry in results[:3])

    def _analyzer(self, args):
        path, _ = self._source({"path": args.get("path")})
        for key in ("line", "column"):
            if not isinstance(args.get(key), int) or args[key] < 1:
                raise ToolError("'{k}' must be a positive (1-based) integer".format(k=key))
        return self.engine().analyzer(path), args["line"] - 1, args["column"] - 1

    def tool_hover(self, args):
        analyzer, line, col = self._analyzer(args)
        result = analyzer.hover(line, col)
        return result[0] if result else "(no information at this position)"

    def _locations(self, locs):
        from coconut.lsp.cli import format_loc
        if not locs:
            return "(nothing found)"
        return "\n".join(format_loc(loc) for loc in locs)

    def tool_definition(self, args):
        analyzer, line, col = self._analyzer(args)
        return self._locations(analyzer.definitions(line, col))

    def tool_references(self, args):
        analyzer, line, col = self._analyzer(args)
        return self._locations(analyzer.references(line, col))

    def tool_symbols(self, args):
        from coconut.lsp.cli import SYMBOL_KIND_NAMES
        from coconut.lsp.symbols import document_symbols, flatten_symbols
        path, _ = self._source({"path": args.get("path")})
        analyzer = self.engine().analyzer(path)
        if analyzer.good is None:
            raise ToolError("the file doesn't compile; run coconut_check for details")
        out = []
        for sym, container in flatten_symbols(document_symbols(analyzer.good)):
            start = sym["selectionRange"]["start"]
            out.append("{l}:{c}: {k} {n}{p}".format(
                l=start["line"] + 1, c=start["character"] + 1, k=SYMBOL_KIND_NAMES.get(sym["kind"], "symbol"),
                n=sym["name"], p=(" (in " + container + ")") if container else "",
            ))
        return "\n".join(out) or "(no symbols)"


def serve_mcp():
    out = sys.stdout
    sys.stdout = sys.stderr  # keep stray prints out of the protocol stream
    return McpServer(sys.stdin, out).run()
