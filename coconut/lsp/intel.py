#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Python-level code intelligence for Coconut, by running jedi over the compiled Python.

A Coconut document is analyzed against its most recent successful compile. Positions are mapped
source -> compiled -> source using the compiler's line-number comments (see sourcemap.py). When
the line under the cursor has been edited since that compile (the usual case while typing), the
expression being typed is spliced into the compiled code at the matching position and scope.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import re
import sys

from coconut.lsp import docs
from coconut.lsp.sourcemap import (
    CompiledDocument,
    LineDiff,
    leading_whitespace,
    parse_line_map,
    word_at,
    word_occurrences,
)
from coconut.lsp.symbols import COCONUT_EXTENSIONS, find_definition_in_text

try:
    import jedi
except Exception:  # pragma: no cover - not installed, or incompatible with this Python
    jedi = None

# LSP CompletionItemKind
COMPLETION_KINDS = {
    "module": 9, "class": 7, "instance": 6, "function": 3, "param": 6, "path": 17,
    "keyword": 14, "property": 10, "statement": 6,
}
KIND_SNIPPET = 15
KIND_KEYWORD = 14

# a dotted expression immediately before the cursor, e.g. "os.path.jo" or "self."
DOTTED_EXPR_RE = re.compile(r"((?:[A-Za-z_]\w*\s*\.\s*)*[A-Za-z_]?\w*)$")
def _matching_open(text, close_idx):
    """Index of the bracket opening the one at close_idx (scanning backwards), or None."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    i = close_idx
    while i >= 0:
        c = text[i]
        if c in pairs:
            stack.append(pairs[c])
        elif c in "([{":
            if not stack or stack.pop() != c:
                return None
            if not stack:
                return i
        elif c in "'\"":
            start = _string_start(text, i)
            if start is None:
                return None
            i = start
        i -= 1
    return None


def _string_start(text, end_quote_idx):
    """Index of the start (including any prefix) of the string literal ending at end_quote_idx."""
    q = text[end_quote_idx]
    i = end_quote_idx - 1
    while i >= 0:
        if text[i] == q and (i == 0 or text[i - 1] != "\\"):
            while i > 0 and text[i - 1] in "rRbBfFuU":
                i -= 1
            return i
        i -= 1
    return None


def trailing_expression(text):
    """The primary expression ending at the end of text, e.g. 'shapes[0].center.' or 'f(x).y'."""
    i = len(text)
    while i > 0:
        c = text[i - 1]
        if c.isalnum() or c == "_" or c == ".":
            i -= 1
        elif c in ")]}":
            j = _matching_open(text, i - 1)
            if j is None:
                break
            i = j
            # a call/subscript needs something before it, unless it's a parenthesized/literal expression
        elif c in "'\"":
            j = _string_start(text, i - 1)
            if j is None:
                break
            i = j
        else:
            break
    expr = text[i:]
    # Coconut's implicit partials ('.attr') and operators like '..>' can't be completed as expressions
    return expr.lstrip(".")


IMPORT_LINE_RE = re.compile(r"^\s*(from\s+[\w.]+\s+import\b.*|from\s+[\w.]*|import\s+.*)$")


def jedi_available():
    return jedi is not None


def compiled_path_for(path):
    """The (virtual) path of the compiled Python file for a Coconut source path."""
    base, ext = os.path.splitext(path)
    return base + ".py"


def is_comment_or_string_position(line, col):
    """Rough check for whether col in line is inside a comment or a (single-line) string."""
    prefix = line[:col]
    in_str = None
    i = 0
    while i < len(prefix):
        c = prefix[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if prefix.startswith(in_str, i):
                i += len(in_str)
                in_str = None
                continue
        elif c in "'\"":
            in_str = prefix[i:i + 3] if prefix[i:i + 3] in ("'''", '"""') else c
            i += len(in_str)
            continue
        elif c == "#":
            return True
        i += 1
    return in_str is not None


class Analyzer(object):
    """Code intelligence for one document state.

    text: the current document text; good: the last successfully compiled CompiledDocument (or None)."""

    def __init__(self, path, text, good=None, workspace_roots=(), overlay=None):
        self.path = path
        self.text = text
        self.lines = text.splitlines()
        if text.endswith("\n") or not self.lines:
            self.lines.append("")
        self.good = good
        self.diff = LineDiff(good.source_lines, self.lines) if good is not None else None
        self.workspace_roots = [r for r in workspace_roots if r]
        self.overlay = overlay
        if overlay is not None:
            self.compiled_path = overlay.script_path(path, self.workspace_roots)
        else:
            self.compiled_path = compiled_path_for(path)
        self._project = None

    # ------------------------------------------------------------------ jedi plumbing

    def project(self):
        if self._project is None and jedi is not None:
            root = None
            for r in self.workspace_roots:
                if os.path.abspath(self.path).startswith(os.path.abspath(r)):
                    root = r
                    break
            if root is None:
                root = os.path.dirname(os.path.abspath(self.path))
            added = []
            if self.overlay is not None:
                added.append(self.overlay.mirror_root(self.overlay.root_for(self.path, self.workspace_roots)))
            try:
                self._project = jedi.Project(root, added_sys_path=added, smart_sys_path=True, load_unsafe_extensions=False)
            except Exception:
                self._project = None
        return self._project

    def script(self, code):
        return jedi.Script(jedi_friendly(code), path=self.compiled_path, project=self.project())

    def line(self, line):
        return self.lines[line] if 0 <= line < len(self.lines) else ""

    # ------------------------------------------------------------------ position mapping

    def to_compiled(self, line, col):
        """Map a current-document position on an identifier to (compiled_code, line0, col, inserted_at).

        inserted_at is the compiled line index of a synthetic line if one was spliced in, else None."""
        if self.good is None:
            return None
        old = self.diff.new_to_old(line)
        if old is not None:
            mapped = self.good.source_to_compiled(old, col)
            if mapped is not None:
                return self.good.compiled, mapped[0], mapped[1], None
        # the line changed since the last good compile: splice in the expression up to the word end
        text = self.line(line)
        found = word_at(text, col)
        if found is None:
            return None
        expr = trailing_expression(text[:found[2]]) or found[0]
        spliced = self.splice(line, expr)
        if spliced is None:
            return None
        code, ins, indent = spliced
        return code, ins, len(indent) + len(expr) - 1, ins

    def splice(self, line, expr):
        """Insert expr as a new compiled line in the scope corresponding to source line `line`.

        Returns (code, inserted_line_index, indent) or None."""
        good = self.good
        if good is None:
            return None
        cur_text = self.line(line)
        cur_indent = len(leading_whitespace(cur_text).expandtabs(4)) if cur_text.strip() else None
        prev_old = self.diff.nearest_new_to_old_before(line)

        # where to insert: before the first compiled line that came from after prev_old
        ins = len(good.compiled_lines)
        for ci in range(good.body_start, len(good.line_map)):
            src = good.line_map[ci]
            if src is not None and (prev_old is None or src > prev_old):
                ins = ci
                break

        # what indentation: find the enclosing/sibling statement in the source
        indent = ""
        if cur_indent is None:
            # blank line: use the cursor column's indentation as typed so far
            cur_indent = len(cur_text.expandtabs(4))
        for cand in range(line - 1, -1, -1):
            cand_text = self.line(cand)
            stripped = cand_text.strip()
            if not stripped or stripped.startswith("#"):
                continue
            cand_indent = len(leading_whitespace(cand_text).expandtabs(4))
            if cand_indent > cur_indent:
                continue
            old = self.diff.new_to_old(cand)
            if old is None:
                continue
            comp_indent = good.compiled_indent_for(old)
            if comp_indent is None:
                continue
            if cand_indent == cur_indent:
                indent = comp_indent
            else:
                # cand opens the block we're in: use the indentation of its compiled body
                indent = comp_indent + "    "
                group = good.src_to_compiled.get(old, [])
                if group:
                    for ci in range(group[0] + 1, len(good.compiled_lines)):
                        body = good.compiled_line(ci)
                        if body.strip():
                            body_indent = leading_whitespace(body)
                            if len(body_indent) > len(comp_indent):
                                indent = body_indent
                            break
            break
        lines = list(good.compiled_lines)
        lines.insert(ins, indent + expr)
        return "\n".join(lines) + "\n", ins, indent

    def from_compiled_line(self, line0, col, name, inserted_at=None):
        """Map a compiled position in this document back to the current document: (line, start, end)."""
        if inserted_at is not None:
            if line0 == inserted_at:
                return None
            if line0 > inserted_at:
                line0 -= 1
        mapped = self.good.compiled_to_source(line0, col, word=name)
        if mapped is None:
            return None
        old_line, start, end = mapped
        new_line = self.diff.old_to_new(old_line)
        if new_line is None:
            # the definition's line was edited: look for the name nearby in the current text
            new_line = old_line
            occ = word_occurrences(self.line(new_line), name) if name else []
            if not occ:
                return None
            start, end = occ[0], occ[0] + len(name)
        return new_line, start, end

    # ------------------------------------------------------------------ locations

    def name_to_location(self, name, inserted_at=None):
        """Convert a jedi Name into (path, line, start, end) in Coconut terms where possible."""
        module_path = name.module_path
        if module_path is None or name.line is None:
            return None
        module_path = str(module_path)
        if os.path.normcase(module_path) == os.path.normcase(self.compiled_path) and self.good is not None:
            mapped = self.from_compiled_line(name.line - 1, name.column, name.name, inserted_at)
            if mapped is None:
                return None
            return (self.path,) + mapped
        if self.overlay is not None and self.overlay.is_mirror_path(module_path):
            real, from_coconut = self.overlay.to_real(module_path)
            if from_coconut:
                loc = map_into_coconut_file(module_path, real, name.line - 1, name.name)
                if loc is not None:
                    return loc
                return real, 0, 0, 0
            module_path = real
        if module_path.endswith(".py"):
            coco = coconut_source_for(module_path)
            if coco is not None:
                loc = map_into_coconut_file(module_path, coco, name.line - 1, name.name)
                if loc is not None:
                    return loc
        return module_path, name.line - 1, name.column, name.column + len(name.name)

    # ------------------------------------------------------------------ features

    def _jedi_at(self, line, col):
        """Returns (script, jedi_line1, jedi_col, inserted_at) or None."""
        if jedi is None:
            return None
        if self.good is not None:
            mapped = self.to_compiled(line, col)
            if mapped is None:
                return None
            code, cl, cc, inserted_at = mapped
            return self.script(code), cl + 1, cc, inserted_at
        # never compiled successfully: treat the Coconut source as (error-recovered) Python
        return self.script(self.text), line + 1, col, None

    def definitions(self, line, col):
        at = self._jedi_at(line, col)
        locations = []
        if at is not None:
            script, jl, jc, inserted_at = at
            try:
                names = script.goto(jl, jc, follow_imports=True, follow_builtin_imports=False)
            except Exception:
                names = []
            for n in names:
                loc = self.name_to_location(n, inserted_at)
                if loc is not None and loc not in locations:
                    locations.append(loc)
        if not locations:
            locations = self.fallback_definitions(line, col)
        return locations

    def fallback_definitions(self, line, col):
        """Resolve names imported from Coconut modules that jedi can't see (no compiled .py)."""
        found = word_at(self.line(line), col)
        if found is None:
            return []
        word = found[0]
        # local definition in this file
        local = find_definition_in_text(self.text, word)
        results = []
        if local is not None and local[0] != line:
            results.append((self.path, local[0], local[1], local[1] + len(word)))
            return results
        # 'from mod import word' / 'import mod' then 'mod.word'
        text_before = self.line(line)[:found[1]]
        module_attr = re.search(r"([A-Za-z_][\w]*)\s*\.\s*$", text_before)
        for m in re.finditer(r"^\s*from\s+(\.*[\w.]*)\s+import\s+(.+)$", self.text, re.MULTILINE):
            imported = [part.strip().split(" as ") for part in m.group(2).strip("() \\").split(",")]
            for parts in imported:
                if parts and (parts[-1].strip() == word or (len(parts) == 1 and parts[0].strip() == word)):
                    target = resolve_coconut_module(m.group(1), self.path, self.workspace_roots)
                    if target is not None:
                        defn = find_definition_in_file(target, parts[0].strip())
                        results.append((target,) + (defn if defn else (0, 0, 0)))
        if module_attr:
            mod = module_attr.group(1)
            for m in re.finditer(r"^\s*import\s+([\w.]+)(?:\s+as\s+(\w+))?\s*$", self.text, re.MULTILINE):
                if (m.group(2) or m.group(1).split(".")[-1]) == mod:
                    target = resolve_coconut_module(m.group(1), self.path, self.workspace_roots)
                    if target is not None:
                        defn = find_definition_in_file(target, word)
                        if defn:
                            results.append((target,) + defn)
        return results

    def references(self, line, col, include_declaration=True):
        at = self._jedi_at(line, col)
        if at is None or self.good is None:
            return []
        script, jl, jc, inserted_at = at
        try:
            names = script.get_references(jl, jc, include_builtins=False, scope="file")
        except Exception:
            return []
        locations = []
        for n in names:
            if not include_declaration and n.is_definition():
                continue
            loc = self.name_to_location(n, inserted_at)
            if loc is not None and loc[0] == self.path and loc not in locations:
                locations.append(loc)
        locations.sort(key=lambda loc: (loc[1], loc[2]))
        return locations

    def hover(self, line, col):
        """Returns (markdown, (line, start, end)) or None."""
        text = self.line(line)
        found = word_at(text, col)
        if found is None or not (found[1] <= col < found[2] or col == found[2]):
            op = docs.operator_at(text, col)
            if op is not None:
                entry = docs.lookup(op[0])
                return docs.format_entry(entry, max_chars=1800), (line, op[1], op[2])
            return None
        word, start, end = found
        kw = docs.keyword_entry(text, start, end)
        if kw is not None and docs.lookup(kw):
            return docs.format_entry(docs.lookup(kw), max_chars=1800), (line, start, end)
        parts = []
        coconut_builtin = False
        at = self._jedi_at(line, col)
        if at is not None:
            script, jl, jc, inserted_at = at
            try:
                names = script.help(jl, jc)
            except Exception:
                names = []
            for n in names[:1]:
                mp = str(n.module_path or "")
                coconut_builtin = "__coconut__" in mp or n.module_name in ("__coconut__", "coconut.__coconut__")
                entry = docs.lookup(word) if coconut_builtin else None
                signature = docs.signature(entry) if entry is not None else None
                if signature is not None:
                    # Coconut's documented signature reads better than the typed stub's overloads
                    parts.append("```python\n" + signature + "\n```")
                    try:
                        doc = escape_docstring(n.docstring(raw=True).strip())
                    except Exception:
                        doc = ""
                    parts[-1] += "\n\n" + (doc or docs.format_entry(entry, include_example=False, max_chars=800))
                    parts[-1] += "\n\n[Coconut documentation](" + entry["url"] + ")"
                    return parts[0], (line, start, end)
                formatted = format_jedi_name(n, script, jl, jc)
                if "_coconut_match_" in formatted or "_coconut_sentinel" in formatted:
                    formatted = self.pattern_function_hover(n, line, col) or formatted
                parts.append(formatted)
        entry = docs.lookup(word)
        if entry is not None and (coconut_builtin or not parts):
            parts.append(docs.format_entry(entry, include_example=not parts, max_chars=1500))
        parts = [p for p in parts if p]
        if not parts:
            return None
        return "\n\n---\n\n".join(parts), (line, start, end)

    def pattern_function_hover(self, n, line, col):
        """Hover text for a pattern-matching function: its Coconut definitions instead of the
        compiled (*args, **kwargs) signature."""
        locs = [loc for loc in self.definitions(line, col) if loc[0].endswith(COCONUT_EXTENSIONS)]
        if not locs:
            return None
        path, def_line = locs[0][0], locs[0][1]
        if path == self.path:
            lines = self.lines
        else:
            try:
                with open(path, encoding="utf-8") as f:
                    lines = f.read().splitlines()
            except (OSError, UnicodeDecodeError):
                return None
        name = n.name
        shown = []
        first = lines[def_line] if def_line < len(lines) else ""
        if re.match(r"^\s*(?:\w+\s+)*case\s+def\b", first) or re.match(r"^\s*case\s+def\b", first):
            indent = len(first) - len(first.lstrip())
            shown.append(first.rstrip())
            for following in lines[def_line + 1:]:
                if following.strip() and len(following) - len(following.lstrip()) <= indent:
                    break
                if re.match(r"^\s*(case|type)\s*\(", following):
                    shown.append(following.rstrip())
        else:
            pattern = re.compile(r"^\s*(?:(?:async|match|addpattern|case|copyclosure|yield)\s+)*def\s+" + re.escape(name) + r"\b")
            shown = [l.rstrip() for l in lines if pattern.match(l)]
        if not shown:
            return None
        if len(shown) > 12:
            shown = shown[:12] + ["..."]
        text = "\n".join(shown)
        dedent = min(len(l) - len(l.lstrip()) for l in shown if l.strip())
        text = "\n".join(l[dedent:] for l in shown)
        doc = ""
        try:
            doc = escape_docstring(n.docstring(raw=True).strip())
        except Exception:
            pass
        return "```coconut\n" + text + "\n```\n\npattern-matching function" + ("\n\n" + doc if doc else "")

    def completions(self, line, col):
        """Returns a list of LSP CompletionItems."""
        text = self.line(line)[:col]
        if is_comment_or_string_position(text, len(text)):
            return []
        import_m = IMPORT_LINE_RE.match(text)
        if import_m:
            expr = text.strip()
        else:
            expr = trailing_expression(text)
            # don't complete right after a number (e.g. "1.")
            if re.match(r"^[\d.]+$", expr) or (expr == "" and re.search(r"(?<!\.)\.$", text)):
                return []
        prefix_m = re.search(r"\w*$", text)
        prefix = prefix_m.group(0) if prefix_m else ""
        items = []
        seen = set()
        if jedi is not None:
            try:
                if self.good is not None:
                    code, ins, indent = self.splice(line, expr)
                    script = self.script(code)
                    comps = script.complete(ins + 1, len(indent) + len(expr))
                else:
                    script = self.script(self.text)
                    comps = script.complete(line + 1, col)
            except Exception:
                comps = []
            for c in comps:
                name = c.name
                if name.startswith("_coconut") or name in seen:
                    continue
                seen.add(name)
                item = {
                    "label": name,
                    "kind": COMPLETION_KINDS.get(c.type, 6),
                    "sortText": ("z" if name.startswith("_") else "a") + name.lower(),
                }
                if c.type == "keyword":
                    item["kind"] = KIND_KEYWORD
                # only global names can be Coconut built-ins (not e.g. a tuple's .count method)
                entry = docs.lookup(name) if "." not in expr and not import_m else None
                if entry is not None and "__coconut__" in (c.module_name or "") + str(c.module_path or ""):
                    item["detail"] = "Coconut built-in"
                    item["documentation"] = {"kind": "markdown", "value": docs.format_entry(entry, include_example=False, max_chars=600)}
                items.append(item)
        if "." not in expr and not import_m:
            for kw in docs.COCONUT_KEYWORDS + ("match def", "case def", "addpattern def", "copyclosure def"):
                if kw.startswith(prefix) and kw not in seen:
                    seen.add(kw)
                    item = {"label": kw, "kind": KIND_KEYWORD, "sortText": "b" + kw}
                    entry = docs.lookup(kw)
                    if entry is not None:
                        item["documentation"] = {"kind": "markdown", "value": docs.format_entry(entry, include_example=False, max_chars=600)}
                    items.append(item)
            if jedi is None:
                import keyword
                import builtins
                for name in keyword.kwlist + [n for n in dir(builtins) if not n.startswith("_")] + list(docs.all_docs()):
                    if re.match(r"^\w+$", name) and name.startswith(prefix) and name not in seen:
                        seen.add(name)
                        items.append({"label": name, "kind": KIND_KEYWORD if keyword.iskeyword(name) else 3})
        return items

    def signature_help(self, line, col):
        if jedi is None:
            return None
        text = self.line(line)[:col]
        # find the innermost unclosed '(' on this line
        depth = 0
        open_idx = None
        for i in range(len(text) - 1, -1, -1):
            c = text[i]
            if c in ")]}":
                depth += 1
            elif c in "([{":
                if depth == 0:
                    if c == "(":
                        open_idx = i
                    break
                depth -= 1
        if open_idx is None:
            return None
        callee = trailing_expression(text[:open_idx].rstrip("$"))
        if not callee or not re.match(r"[A-Za-z_]", callee):
            return None
        args = text[open_idx + 1:]
        expr = callee + "(" + args
        try:
            if self.good is not None:
                code, ins, indent = self.splice(line, expr)
                script = self.script(code)
                sigs = script.get_signatures(ins + 1, len(indent) + len(expr))
            else:
                script = self.script(self.text)
                sigs = script.get_signatures(line + 1, col)
        except Exception:
            return None
        if not sigs:
            return None
        signatures = []
        active = 0
        for sig in sigs[:5]:
            params = [{"label": p.to_string()} for p in sig.params]
            doc = sig.docstring(raw=True)
            signature = {"label": sig.to_string(), "parameters": params}
            entry = docs.lookup(sig.name)
            if entry is not None:
                signature["documentation"] = {"kind": "markdown", "value": docs.format_entry(entry, include_example=False, max_chars=800)}
            elif doc:
                signature["documentation"] = {"kind": "plaintext", "value": doc}
            if sig.index is not None:
                signature["activeParameter"] = sig.index
                active = sig.index
            signatures.append(signature)
        return {"signatures": signatures, "activeSignature": 0, "activeParameter": active}

    def rename_locations(self, line, col):
        """Locations to rename for the symbol at (line, col), or raise ValueError."""
        found = word_at(self.line(line), col)
        if found is None:
            raise ValueError("no symbol at this position")
        refs = self.references(line, col)
        if not refs:
            raise ValueError("couldn't find references to rename (does the file compile?)")
        definitions = self.definitions(line, col)
        if any(d[0] != self.path for d in definitions):
            raise ValueError("can only rename symbols defined in this file")
        for path, l, s, e in refs:
            if self.line(l)[s:e] != found[0]:
                raise ValueError("couldn't map all references back to the Coconut source")
        return found[0], refs


_HEADER_IMPORT = "from coconut.__coconut__ import *\n"
_TYPED_DATA_RE = re.compile(r'_coconut\.typing\.NamedTuple\("(\w+)", \[(.*)\]\)\)')


def jedi_friendly(code):
    """Rewrite compiled code (without changing its line structure) so jedi understands it better:
    jedi can infer fields of collections.namedtuple classes, but not through Coconut's '_coconut'
    alias or the functional typing.NamedTuple form used for 'data' types."""
    if _HEADER_IMPORT not in code:
        return code
    code = code.replace(_HEADER_IMPORT, "from coconut.__coconut__ import *; import collections as _coconut_ls_collections\n", 1)
    code = code.replace("_coconut.collections.namedtuple(", "_coconut_ls_collections.namedtuple(")

    def typed(m):
        fields = re.findall(r'\("(\w+)", ', m.group(2))
        return '_coconut_ls_collections.namedtuple("{n}", {f}))'.format(n=m.group(1), f=repr(tuple(fields)))

    return _TYPED_DATA_RE.sub(typed, code)


def escape_docstring(doc):
    """Escape a Python docstring for display as Markdown (e.g. so __x__ isn't rendered as bold),
    leaving `code spans` and indented/fenced code alone."""
    out = []
    in_fence = False
    for line in doc.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence or line.startswith("    ") or line.lstrip().startswith(">>>"):
            out.append(line)
            continue
        parts = re.split(r"(`[^`]*`)", line)
        for i in range(0, len(parts), 2):
            parts[i] = re.sub(r"([_<>\\])", r"\\\1", parts[i])
        out.append("".join(parts))
    return "\n".join(out)


def format_jedi_name(n, script=None, line=None, col=None):
    """Markdown hover text for a jedi Name."""
    header = None
    try:
        if n.type in ("function", "class"):
            sigs = n.get_signatures()
            if sigs:
                prefix = "class " if n.type == "class" else "def "
                header = "\n".join(prefix + s.to_string() for s in sigs[:3])
        if header is None:
            if n.type == "module":
                header = "module " + (n.full_name or n.name)
            elif n.type in ("instance", "statement", "param"):
                types = []
                if script is not None:
                    try:
                        types = [t.name for t in script.infer(line, col)][:3]
                    except Exception:
                        types = []
                header = n.name + (": " + " | ".join(dict.fromkeys(types)) if types else "")
                if n.type == "param":
                    header = "(parameter) " + header
                elif n.type == "statement":
                    header = "(variable) " + header
            else:
                header = n.description
    except Exception:
        header = n.name
    docstring = ""
    try:
        docstring = n.docstring(raw=True) if n.type != "module" else n.docstring(raw=True).split("\n\n")[0]
    except Exception:
        pass
    parts = ["```python\n" + header + "\n```"]
    if docstring and docstring.strip() != header.strip():
        parts.append(escape_docstring(docstring.strip()))
    return "\n\n".join(parts)


def coconut_source_for(py_path):
    """The Coconut source file a compiled .py file came from, if one exists next to it."""
    base = os.path.splitext(py_path)[0]
    for ext in COCONUT_EXTENSIONS:
        if os.path.exists(base + ext):
            return base + ext
    return None


def map_into_coconut_file(py_path, coco_path, py_line, name):
    """Map a line of a compiled .py file to its .coco source: (coco_path, line, start, end) or None."""
    try:
        with open(coco_path, encoding="utf-8") as f:
            coco_text = f.read()
    except (OSError, UnicodeDecodeError):
        return None
    coco_lines = coco_text.splitlines()
    try:
        with open(py_path, encoding="utf-8") as f:
            py_text = f.read()
        line_map = parse_line_map(py_text)
    except (OSError, UnicodeDecodeError):
        line_map = []
    src = line_map[py_line] if 0 <= py_line < len(line_map) else None
    if src is not None and 0 <= src < len(coco_lines):
        occ = word_occurrences(coco_lines[src], name)
        if occ:
            return coco_path, src, occ[0], occ[0] + len(name)
    defn = find_definition_in_text(coco_text, name)
    if defn is not None:
        return coco_path, defn[0], defn[1], defn[1] + len(name)
    return None


def find_definition_in_file(path, name):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return None
    defn = find_definition_in_text(text, name)
    if defn is None:
        return None
    return defn[0], defn[1], defn[1] + len(name)


def resolve_coconut_module(module, from_path, roots):
    """Find the Coconut source file for an import like '.mod', 'pkg.mod' from from_path."""
    dots = len(module) - len(module.lstrip("."))
    parts = [p for p in module.lstrip(".").split(".") if p]
    bases = []
    if dots:
        base = os.path.dirname(os.path.abspath(from_path))
        for _ in range(dots - 1):
            base = os.path.dirname(base)
        bases.append(base)
    else:
        bases.append(os.path.dirname(os.path.abspath(from_path)))
        bases.extend(roots)
        bases.extend(p for p in sys.path if p and os.path.isdir(p))
    for base in bases:
        target = os.path.join(base, *parts) if parts else base
        for ext in COCONUT_EXTENSIONS:
            if parts and os.path.isfile(target + ext):
                return target + ext
            init = os.path.join(target, "__init__" + ext)
            if os.path.isfile(init):
                return init
    return None
