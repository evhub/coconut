#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Document symbols (from the compiled AST) and a lightweight workspace symbol index.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import ast
import os
import re


# LSP SymbolKind values
KIND_FILE = 1
KIND_MODULE = 2
KIND_CLASS = 5
KIND_METHOD = 6
KIND_PROPERTY = 7
KIND_FUNCTION = 12
KIND_VARIABLE = 13
KIND_CONSTANT = 14
KIND_STRUCT = 23
KIND_OPERATOR = 25

COCONUT_EXTENSIONS = (".coco", ".coc", ".coconut")

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", "__coconut_cache__", ".mypy_cache",
    ".pytest_cache", ".tox", ".nox", ".venv", "venv", "env", ".env", "build", "dist", "site-packages",
    ".eggs", ".idea", ".vscode",
}


def _range(line, start, end_line=None, end=None):
    return {
        "start": {"line": line, "character": start},
        "end": {"line": line if end_line is None else end_line, "character": start if end is None else end},
    }


def document_symbols(doc, line_mapper=None):
    """Build hierarchical LSP DocumentSymbols for a CompiledDocument.

    line_mapper optionally maps a source line of the compiled document to the current document."""
    try:
        tree = ast.parse(doc.compiled)
    except SyntaxError:
        return []
    mapper = line_mapper or (lambda line: line)

    def src_of(lineno):
        idx = lineno - 1
        if 0 <= idx < len(doc.line_map):
            return doc.line_map[idx]
        return None

    def last_src_line(node):
        end = getattr(node, "end_lineno", None) or node.lineno
        for ln in range(end, node.lineno - 1, -1):
            src = src_of(ln)
            if src is not None:
                return src
        return src_of(node.lineno)

    def make(name, kind, node, parent_src):
        src = src_of(node.lineno)
        if src is None or name.startswith("_coconut"):
            return None
        # skip compiler-generated names that don't appear in the source
        # (e.g. a data class's generated methods); allow adjacent lines for defs, since Coconut
        # sometimes attributes a def to the line before it
        located = doc.locate_name(src, name, neighbors=kind in (KIND_FUNCTION, KIND_METHOD, KIND_CLASS, KIND_STRUCT))
        if located is None:
            return None
        src, col = located
        if parent_src is not None and src == parent_src and kind in (KIND_METHOD, KIND_FUNCTION):
            return None
        cur = mapper(src)
        if cur is None:
            return None
        src_line = doc.source_line(src)
        end_src = last_src_line(node)
        end_cur = mapper(end_src) if end_src is not None else None
        if end_cur is None or end_cur < cur:
            end_cur = cur
            end_text = src_line
        else:
            end_text = doc.source_line(end_src)
        detail = ""
        if kind == KIND_STRUCT:
            detail = "data"
        elif re.search(r"\bmatch\s+def\b|\bcase\s+def\b|\baddpattern\s+def\b", src_line):
            detail = "pattern-matching function"
        return {
            "name": name,
            "detail": detail,
            "kind": kind,
            "range": _range(cur, len(src_line) - len(src_line.lstrip()), end_cur, len(end_text)),
            "selectionRange": _range(cur, col, cur, col + len(name)),
            "children": [],
        }

    def visit(body, parent_src, in_class):
        symbols = []
        seen = {}
        for node in body:
            sym = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sym = make(node.name, KIND_METHOD if in_class else KIND_FUNCTION, node, parent_src)
                if sym is not None:
                    sym["children"] = visit(node.body, src_of(node.lineno), False)
            elif isinstance(node, ast.ClassDef):
                is_data = any("_coconut_is_data" in ast.dump(stmt) for stmt in node.body[:6])
                sym = make(node.name, KIND_STRUCT if is_data else KIND_CLASS, node, parent_src)
                if sym is not None:
                    sym["children"] = visit(node.body, src_of(node.lineno), True)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)) and parent_src is None or (
                in_class and isinstance(node, (ast.Assign, ast.AnnAssign))
            ):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    for name_node in ast.walk(target):
                        if isinstance(name_node, ast.Name):
                            kind = KIND_CONSTANT if name_node.id.isupper() else (KIND_PROPERTY if in_class else KIND_VARIABLE)
                            var = make(name_node.id, kind, node, parent_src)
                            if var is not None and name_node.id not in seen:
                                seen[name_node.id] = var
                                symbols.append(var)
                continue
            elif isinstance(node, (ast.If, ast.Try, ast.With, ast.For, ast.While)) and not in_class and parent_src is None:
                # e.g. top-level definitions under 'if TYPE_CHECKING:' or try/except imports
                nested = []
                for field in ("body", "orelse", "finalbody"):
                    nested += visit(getattr(node, field, []) or [], parent_src, in_class)
                for handler in getattr(node, "handlers", []) or []:
                    nested += visit(handler.body, parent_src, in_class)
                for s in nested:
                    if s["name"] not in seen:
                        seen[s["name"]] = s
                        symbols.append(s)
                continue
            if sym is not None:
                if sym["name"] in seen and seen[sym["name"]]["kind"] == sym["kind"]:
                    # pattern-matching functions defined across several 'addpattern'/'case def's
                    prev = seen[sym["name"]]
                    if sym["range"]["end"]["line"] > prev["range"]["end"]["line"]:
                        prev["range"]["end"] = sym["range"]["end"]
                    continue
                seen[sym["name"]] = sym
                symbols.append(sym)
        return symbols

    return visit(tree.body, None, False)


def flatten_symbols(symbols, container=None):
    """Turn hierarchical DocumentSymbols into (symbol, container_name) pairs."""
    for sym in symbols:
        yield sym, container
        for child in flatten_symbols(sym.get("children", []), sym["name"]):
            yield child


# -----------------------------------------------------------------------------------------------------------------------
# REGEX-BASED INDEX (for files that aren't open; much faster than compiling every file)
# -----------------------------------------------------------------------------------------------------------------------

DEF_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?:@[^\n]*\n[ \t]*)*"
    r"(?:(?:async|match|case|addpattern|copyclosure|yield)\s+)*"
    r"(?P<kw>def|class|data|operator)\s+(?P<name>[A-Za-z_]\w*)",
    re.MULTILINE,
)
ASSIGN_RE = re.compile(r"^(?P<name>[A-Za-z_]\w*)\s*(?::[^=\n]+)?=(?!=)", re.MULTILINE)
KW_KIND = {"def": KIND_FUNCTION, "class": KIND_CLASS, "data": KIND_STRUCT, "operator": KIND_OPERATOR}


def scan_symbols(text):
    """Quickly find definitions in Coconut source: yields (name, kind, line, col, indent)."""
    line_starts = [0]
    for m in re.finditer(r"\n", text):
        line_starts.append(m.end())

    def pos(offset):
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo, offset - line_starts[lo]

    found = []
    for m in DEF_RE.finditer(text):
        line, col = pos(m.start("name"))
        indent = len(m.group("indent").expandtabs(4))
        kind = KW_KIND[m.group("kw")]
        if kind == KIND_FUNCTION and indent > 0:
            kind = KIND_METHOD
        found.append((m.group("name"), kind, line, col, indent))
    for m in ASSIGN_RE.finditer(text):
        name = m.group("name")
        if name in ("match", "case", "data", "if", "elif", "while", "return"):
            continue
        line, col = pos(m.start("name"))
        found.append((name, KIND_CONSTANT if name.isupper() else KIND_VARIABLE, line, col, 0))
    found.sort(key=lambda s: (s[2], s[3]))
    return found


def iter_coconut_files(root, max_files=5000):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith(COCONUT_EXTENSIONS):
                yield os.path.join(dirpath, fn)
                count += 1
                if count >= max_files:
                    return


class WorkspaceIndex(object):
    """Caches regex-scanned symbols per file, keyed by mtime."""

    def __init__(self):
        self.cache = {}

    def file_symbols(self, path):
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            self.cache.pop(path, None)
            return []
        cached = self.cache.get(path)
        if cached is not None and cached[0] == mtime:
            return cached[1]
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            text = ""
        symbols = scan_symbols(text)
        self.cache[path] = (mtime, symbols)
        return symbols

    def search(self, roots, query, open_docs=None, limit=500):
        """Find symbols whose names fuzzy-match query across all Coconut files under roots.

        open_docs maps path -> list of (name, kind, line, col, container) for open documents."""
        open_docs = open_docs or {}
        results = []
        seen_paths = set()
        for path, syms in open_docs.items():
            seen_paths.add(os.path.normcase(os.path.abspath(path)))
            for name, kind, line, col, container in syms:
                if fuzzy_match(query, name):
                    results.append((name, kind, path, line, col, container))
        for root in roots:
            for path in iter_coconut_files(root):
                if os.path.normcase(os.path.abspath(path)) in seen_paths:
                    continue
                seen_paths.add(os.path.normcase(os.path.abspath(path)))
                for name, kind, line, col, indent in self.file_symbols(path):
                    if fuzzy_match(query, name):
                        results.append((name, kind, path, line, col, None))
                if len(results) >= limit:
                    return results[:limit]
        return results[:limit]


def fuzzy_match(query, name):
    """Subsequence match, case-insensitive (like most editors' symbol search)."""
    if not query:
        return True
    q = query.lower()
    n = name.lower()
    i = 0
    for ch in n:
        if i < len(q) and ch == q[i]:
            i += 1
    return i == len(q)


def find_definition_in_text(text, name):
    """Find the (line, col) of a top-level-ish definition of name in Coconut source text."""
    best = None
    for sym_name, kind, line, col, indent in scan_symbols(text):
        if sym_name == name:
            if best is None or indent < best[2]:
                best = (line, col, indent)
    return (best[0], best[1]) if best else None
