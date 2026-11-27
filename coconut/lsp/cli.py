#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Command-line interface for the Coconut language server, plus one-shot commands
for scripts, CI, and AI agents (run with python -m coconut.lsp).
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import argparse
import io
import json
import os
import sys


USAGE = """\
examples:
    coconut --lsp                                # run the language server over stdio
    python -m coconut.lsp                        # same
    python -m coconut.lsp check src/ a.coco      # report errors/warnings (exit code 1 on errors)
    python -m coconut.lsp compile a.coco         # print the compiled Python
    python -m coconut.lsp hover a.coco 12 5      # type/doc info at line 12, column 5 (1-based)
    python -m coconut.lsp definition a.coco 12 5
    python -m coconut.lsp references a.coco 12 5
    python -m coconut.lsp symbols a.coco         # outline of a file
    python -m coconut.lsp docs "|>"              # Coconut documentation for a built-in/keyword/operator
    python -m coconut.lsp mcp                    # run as an MCP server (for AI agents)

Lines and columns on the command line are 1-based; JSON output (--json) uses 1-based lines and
columns too, so results can be fed straight back into these commands.
"""

SEVERITY_NAMES = {1: "error", 2: "warning", 3: "info", 4: "hint"}


def read_file(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def collect_files(paths):
    from coconut.lsp.symbols import iter_coconut_files
    files = []
    for path in paths:
        if os.path.isdir(path):
            files.extend(sorted(iter_coconut_files(path, max_files=100000)))
        else:
            files.append(path)
    return files


class Engine(object):
    """Compiles and analyzes files in-process (shared by the CLI and the MCP server)."""

    def __init__(self, settings=None, roots=None):
        from coconut.lsp.worker import InProcessCompiler
        self.settings = settings or {}
        self.compiler = InProcessCompiler()
        self.roots = roots or [os.getcwd()]
        self.cache = {}
        from coconut.lsp.overlay import Overlay
        self.overlay = Overlay(lambda text: self.compiler.call("compile", {"code": text, "settings": dict(self.settings, lint=False)}).get("compiled"))

    def compile(self, path, text=None):
        from coconut.lsp.sourcemap import CompiledDocument
        path = os.path.abspath(path)
        if text is None:
            text = read_file(path)
        key = (path, text, json.dumps(self.settings, sort_keys=True))
        if key not in self.cache:
            from coconut.lsp.compiler import first_error_line, repair_source
            result = self.compiler.call("compile", {"code": text, "settings": self.settings})
            good = CompiledDocument(text, result["compiled"]) if result.get("compiled") is not None else None
            repaired, diags = text, result.get("diagnostics", [])
            for _ in range(3):
                if good is not None or result.get("fatal"):
                    break
                line = first_error_line(diags)
                repaired = repair_source(repaired, line) if line is not None else None
                if repaired is None:
                    break
                attempt = self.compiler.call("compile", {"code": repaired, "settings": dict(self.settings, lint=False)})
                diags = attempt.get("diagnostics", [])
                if attempt.get("compiled") is not None:
                    good = CompiledDocument(repaired, attempt["compiled"])
            self.cache[key] = (result, good)
        return self.cache[key]

    def analyzer(self, path, text=None):
        from coconut.lsp.intel import Analyzer
        path = os.path.abspath(path)
        if text is None:
            text = read_file(path)
        result, good = self.compile(path, text)
        from coconut.lsp.intel import jedi_available
        if jedi_available():
            try:
                self.overlay.prepare(path, text, self.roots)
            except Exception:
                pass
        return Analyzer(path, text, good, self.roots, self.overlay)

    def check(self, path, text=None):
        result, good = self.compile(path, text)
        if result.get("fatal"):
            raise RuntimeError(result["fatal"])
        diagnostics = list(result.get("diagnostics", []))
        if self.settings.get("mypy") and result.get("compiled") is not None:
            from coconut.lsp.typecheck import mypy_available, run_mypy
            if not mypy_available():
                raise RuntimeError("mypy isn't installed (run: {exe} -m pip install mypy)".format(exe=sys.executable))
            if text is None:
                text = read_file(path)
            diagnostics += run_mypy(os.path.abspath(path), text, result["compiled"], self.overlay, self.roots)
        return diagnostics


def diag_to_json(path, diag):
    start, end = diag["range"]["start"], diag["range"]["end"]
    return {
        "file": path,
        "line": start["line"] + 1,
        "column": start["character"] + 1,
        "end_line": end["line"] + 1,
        "end_column": end["character"] + 1,
        "severity": SEVERITY_NAMES.get(diag.get("severity"), "error"),
        "source": diag.get("source", "coconut"),
        "code": diag.get("code"),
        "message": diag.get("message", ""),
    }


def loc_to_json(loc):
    path, line, start, end = loc
    return {"file": path, "line": line + 1, "column": start + 1, "end_column": end + 1}


def format_loc(loc, with_text=True):
    path, line, start, end = loc
    text = ""
    if with_text:
        try:
            text = read_file(path).splitlines()[line].strip()
        except Exception:
            text = ""
    return "{p}:{l}:{c}{t}".format(p=path, l=line + 1, c=start + 1, t=(": " + text) if text else "")


def make_parser():
    parser = argparse.ArgumentParser(
        prog="python -m coconut.lsp",
        description="Coconut language server and code-intelligence CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=USAGE,
    )
    parser.add_argument("--version", action="version", version="Coconut language server " + VERSION_STR)
    sub = parser.add_subparsers(dest="command")

    def common(p, json_flag=True):
        p.add_argument("--target", default=None, help="Python version to target (default: sys)")
        p.add_argument("--strict", action="store_true", help="enable Coconut's --strict style checks")
        p.add_argument("--no-lint", action="store_true", help="don't run pyflakes on the compiled code")
        if json_flag == "check":
            p.add_argument("--mypy", action="store_true", help="also type-check the compiled code with mypy")
        if json_flag:
            p.add_argument("--json", action="store_true", help="output JSON")

    sub.add_parser("serve", help="run the language server over stdio (the default)")
    p = sub.add_parser("check", help="report compiler errors/warnings and lint results")
    p.add_argument("paths", nargs="+", help="Coconut files or directories")
    p.add_argument("--warnings-as-errors", "-W", action="store_true", help="exit with code 1 on warnings too")
    common(p, json_flag="check")
    p = sub.add_parser("compile", help="print the compiled Python for a file")
    p.add_argument("file")
    p.add_argument("--no-line-comments", action="store_true", help="strip the '#N (line in Coconut source)' comments")
    common(p, json_flag=False)
    for name, help_text in (
        ("hover", "show type/documentation information at a position"),
        ("definition", "find where the symbol at a position is defined"),
        ("references", "find references to the symbol at a position (within its file)"),
        ("complete", "list completions at a position"),
        ("signature", "show the signature of the call at a position"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("file")
        p.add_argument("line", type=int, help="1-based line")
        p.add_argument("column", type=int, help="1-based column")
        common(p)
    p = sub.add_parser("symbols", help="list the symbols defined in a file")
    p.add_argument("file")
    common(p)
    p = sub.add_parser("docs", help="look up Coconut documentation for a built-in, keyword, or operator")
    p.add_argument("query", nargs="?", default=None)
    p.add_argument("--list", action="store_true", help="list all documented names")
    p.add_argument("--json", action="store_true")
    sub.add_parser("mcp", help="run as a Model Context Protocol server over stdio")
    sub.add_parser("info", help="show the Coconut/Python/jedi/pyflakes versions in use")
    return parser


def settings_from(args):
    settings = {}
    if getattr(args, "target", None):
        settings["target"] = args.target
    if getattr(args, "strict", False):
        settings["strict"] = True
    if getattr(args, "no_lint", False):
        settings["lint"] = False
    if getattr(args, "mypy", False):
        settings["mypy"] = True
    return settings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    # flags that LSP clients commonly pass when launching a server over stdio
    argv = [a for a in argv if a not in ("--stdio", "--lsp") and not a.startswith("--clientProcessId")]
    parser = make_parser()
    args = parser.parse_args(argv)
    command = args.command or "serve"

    if command == "serve":
        from coconut.lsp.server import serve_stdio
        return serve_stdio()
    if command == "mcp":
        from coconut.lsp.mcp import serve_mcp
        return serve_mcp()
    if command == "info":
        from coconut.lsp.compiler import coconut_info
        from coconut.lsp.intel import jedi_available
        info = coconut_info()
        info["jedi"] = jedi_available()
        print(json.dumps(info, indent=2))
        return 0 if info.get("coconut_version") else 1
    if command == "docs":
        return docs_command(args)

    engine = Engine(settings_from(args))
    try:
        if command == "check":
            return check_command(engine, args)
        if command == "compile":
            result, good = engine.compile(args.file)
            if result.get("fatal"):
                print(result["fatal"], file=sys.stderr)
                return 2
            if good is None:
                for diag in result["diagnostics"]:
                    print(format_diag(args.file, diag), file=sys.stderr)
                return 1
            code = good.compiled
            if args.no_line_comments:
                from coconut.lsp.sourcemap import strip_line_comment
                code = "\n".join(strip_line_comment(line) for line in code.splitlines()) + "\n"
            sys.stdout.write(code)
            return 0
        return position_command(engine, command, args)
    except RuntimeError as err:
        print(str(err), file=sys.stderr)
        return 2


def format_diag(path, diag):
    d = diag_to_json(path, diag)
    d["code"] = " [" + d["code"] + "]" if d["code"] else ""
    return "{file}:{line}:{column}: {severity}: {message}{code}".format(**d)


def check_command(engine, args):
    files = collect_files(args.paths)
    all_diags = []
    exit_code = 0
    for path in files:
        try:
            diags = engine.check(path)
        except (OSError, UnicodeDecodeError) as err:
            diags = [{"range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 0}},
                      "severity": 1, "message": "couldn't read file: " + str(err)}]
        for diag in sorted(diags, key=lambda d: (d["range"]["start"]["line"], d["range"]["start"]["character"])):
            sev = diag.get("severity", 1)
            if sev == 1 or (args.warnings_as_errors and sev == 2):
                exit_code = 1
            if sev == 4 and not args.json:
                continue  # hints (e.g. unused variables) are editor-only in text mode
            all_diags.append(diag_to_json(path, diag))
            if not args.json:
                print(format_diag(path, diag))
    if args.json:
        print(json.dumps({"files_checked": len(files), "diagnostics": all_diags}, indent=2))
    elif not all_diags:
        print("checked {n} file{s}: no problems found".format(n=len(files), s="" if len(files) == 1 else "s"), file=sys.stderr)
    return exit_code


def position_command(engine, command, args):
    analyzer = engine.analyzer(args.file)
    if command == "symbols":
        from coconut.lsp.symbols import document_symbols, flatten_symbols
        syms = document_symbols(analyzer.good) if analyzer.good is not None else []
        rows = []
        for sym, container in flatten_symbols(syms):
            start = sym["selectionRange"]["start"]
            rows.append({"name": sym["name"], "kind": SYMBOL_KIND_NAMES.get(sym["kind"], str(sym["kind"])),
                         "line": start["line"] + 1, "column": start["character"] + 1, "container": container,
                         "detail": sym.get("detail") or None})
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            if analyzer.good is None:
                print("(file doesn't compile; run 'check' for details)", file=sys.stderr)
            for row in rows:
                print("{line}:{column}: {kind} {name}{c}".format(c=(" (in " + row["container"] + ")") if row["container"] else "", **row))
        return 0

    line, col = args.line - 1, args.column - 1
    if command == "hover":
        result = analyzer.hover(line, col)
        if args.json:
            print(json.dumps({"markdown": result[0] if result else None}, indent=2))
        else:
            print(result[0] if result else "(no information)")
        return 0 if result else 1
    if command in ("definition", "references"):
        locs = analyzer.definitions(line, col) if command == "definition" else analyzer.references(line, col)
        if args.json:
            print(json.dumps([loc_to_json(loc) for loc in locs], indent=2))
        else:
            for loc in locs:
                print(format_loc(loc))
            if not locs:
                print("(nothing found)", file=sys.stderr)
        return 0 if locs else 1
    if command == "complete":
        items = analyzer.completions(line, col)
        items.sort(key=lambda i: i.get("sortText", i["label"]))
        if args.json:
            print(json.dumps([{"label": i["label"], "detail": i.get("detail")} for i in items], indent=2))
        else:
            for item in items:
                print(item["label"])
        return 0
    if command == "signature":
        help_ = analyzer.signature_help(line, col)
        if args.json:
            print(json.dumps(help_, indent=2))
        elif help_:
            for sig in help_["signatures"]:
                print(sig["label"])
        else:
            print("(no signature)", file=sys.stderr)
        return 0 if help_ else 1
    raise RuntimeError("unknown command " + command)


def docs_command(args):
    from coconut.lsp import docs
    if args.list or not args.query:
        names = sorted(docs.all_docs())
        if args.json:
            print(json.dumps(names))
        else:
            print("\n".join(names))
        return 0
    results = docs.search(args.query)
    if args.json:
        print(json.dumps([dict(entry, key=key) for key, entry in results], indent=2))
    elif results:
        print("\n\n========\n\n".join(docs.format_entry(entry) for key, entry in results[:3]))
    else:
        print("no Coconut documentation found for " + repr(args.query), file=sys.stderr)
    return 0 if results else 1


SYMBOL_KIND_NAMES = {
    2: "module", 5: "class", 6: "method", 7: "property", 12: "function", 13: "variable",
    14: "constant", 23: "data", 25: "operator",
}
