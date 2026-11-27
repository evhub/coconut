#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Mapping positions between Coconut source and the Python code it compiles to.

Coconut (with line_numbers=True) appends a "#N (line in Coconut source)" comment to every
compiled line, which gives an exact line-level mapping. Columns are recovered by matching
the n-th occurrence of an identifier in the source line with the n-th occurrence of the same
identifier in the compiled lines generated from it (string literals and comments excluded).
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import difflib
import re

LINE_COMMENT_RE = re.compile(r"\s*#(\d+) \(line in Coconut source\)\s*$")
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
STRING_PREFIX_CHARS = "rRbBuUfFtT"


def parse_line_map(compiled):
    """Return, for each compiled line, the 0-based Coconut source line it came from (or None)."""
    line_map = []
    for line in compiled.splitlines():
        m = LINE_COMMENT_RE.search(line)
        line_map.append(int(m.group(1)) - 1 if m else None)
    return line_map


def strip_line_comment(line):
    """Remove the trailing Coconut line-number comment from a compiled line."""
    m = LINE_COMMENT_RE.search(line)
    return line[:m.start()] if m else line


def blank_strings_and_comments(line):
    """Return line with the contents of (non-f-)string literals and comments replaced by spaces,
    preserving length so that column offsets are unchanged."""
    out = list(line)
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == "#":
            for j in range(i, n):
                out[j] = " "
            break
        if c in "'\"":
            # find the string prefix (e.g. f, rb) directly before the quote
            j = i
            while j > 0 and line[j - 1] in STRING_PREFIX_CHARS:
                j -= 1
            prefix = line[j:i].lower()
            if j > 0 and (line[j - 1].isalnum() or line[j - 1] == "_"):
                prefix = ""  # quote follows an identifier; not a prefix
            quote = line[i:i + 3] if line[i:i + 3] in ("'''", '"""') else c
            k = i + len(quote)
            while k < n:
                if line[k] == "\\" and "r" not in prefix:
                    k += 2
                    continue
                if line.startswith(quote, k):
                    break
                k += 1
            end = min(k + len(quote), n)
            if "f" not in prefix and "t" not in prefix:
                for idx in range(i + len(quote), min(k, n)):
                    out[idx] = " "
            i = end
            continue
        i += 1
    return "".join(out)


def word_occurrences(line, word):
    """Columns at which word occurs as a whole identifier in line, ignoring strings and comments."""
    cleaned = blank_strings_and_comments(line)
    return [m.start() for m in IDENT_RE.finditer(cleaned) if m.group(0) == word]


def word_at(line, col):
    """Return (word, start, end) for the identifier at or immediately before col, or None."""
    for m in IDENT_RE.finditer(line):
        if m.start() <= col <= m.end():
            return m.group(0), m.start(), m.end()
    return None


class LineDiff(object):
    """Maps line numbers between two versions of a document (only unchanged lines map)."""

    def __init__(self, old_lines, new_lines):
        self.old_to_new_map = {}
        self.new_to_old_map = {}
        if old_lines == new_lines:
            self.identical = True
            return
        self.identical = False
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    self.old_to_new_map[i1 + k] = j1 + k
                    self.new_to_old_map[j1 + k] = i1 + k

    def old_to_new(self, line):
        if self.identical:
            return line
        return self.old_to_new_map.get(line)

    def new_to_old(self, line):
        if self.identical:
            return line
        return self.new_to_old_map.get(line)

    def nearest_new_to_old_before(self, line):
        """The old line corresponding to the nearest unchanged new line strictly before line."""
        for candidate in range(line - 1, -1, -1):
            old = self.new_to_old(candidate)
            if old is not None:
                return old
        return None


class CompiledDocument(object):
    """A successfully compiled Coconut document with its line mapping."""

    def __init__(self, source, compiled):
        self.source = source
        self.compiled = compiled
        self.source_lines = source.splitlines()
        self.compiled_lines = compiled.splitlines()
        self.line_map = parse_line_map(compiled)
        self.src_to_compiled = {}
        for ci, si in enumerate(self.line_map):
            if si is not None:
                self.src_to_compiled.setdefault(si, []).append(ci)
        # the first compiled line that came from user code (everything before is the header)
        self.body_start = next((i for i, s in enumerate(self.line_map) if s is not None), len(self.line_map))

    def source_line(self, line):
        if 0 <= line < len(self.source_lines):
            return self.source_lines[line]
        return ""

    def compiled_line(self, line):
        if 0 <= line < len(self.compiled_lines):
            return strip_line_comment(self.compiled_lines[line])
        return ""

    def source_to_compiled(self, line, col):
        """Map a source position on an identifier to the corresponding compiled position, or None."""
        src_line = self.source_line(line)
        found = word_at(src_line, col)
        if found is None:
            return None
        word, start, _ = found
        src_occurrences = word_occurrences(src_line, word)
        try:
            index = src_occurrences.index(start)
        except ValueError:
            index = 0  # the identifier is inside a string/comment (e.g. f-string); best effort
        candidates = []
        for ci in self.src_to_compiled.get(line, []):
            for c in word_occurrences(self.compiled_line(ci), word):
                candidates.append((ci, c))
        if not candidates:
            return None
        ci, c = candidates[min(index, len(candidates) - 1)]
        return ci, c + (col - start)

    def compiled_to_source(self, line, col=None, word=None):
        """Map a compiled position (optionally on identifier word) back to a source position.

        Returns (line, start_col, end_col) or None if the compiled line has no source line."""
        if not 0 <= line < len(self.line_map):
            return None
        src = self.line_map[line]
        if src is None:
            return None
        src_line = self.source_line(src)
        if word is None and col is not None:
            found = word_at(self.compiled_line(line), col)
            if found is not None:
                word = found[0]
        if word:
            # find which occurrence of word (across all compiled lines from this source line) this is
            index = 0
            for ci in self.src_to_compiled.get(src, []):
                occ = word_occurrences(self.compiled_line(ci), word)
                if ci == line:
                    if col is not None:
                        index += len([c for c in occ if c + len(word) < col])
                    break
                index += len(occ)
            src_occ = word_occurrences(src_line, word)
            if src_occ:
                start = src_occ[min(index, len(src_occ) - 1)]
                return src, start, start + len(word)
            # Coconut sometimes attributes a statement to an adjacent line (e.g. a 'def' inside a
            # 'data' block is attributed to the 'data' line), so look at the neighboring lines
            for delta in (1, -1, 2, -2):
                near = src + delta
                if 0 <= near < len(self.source_lines):
                    near_occ = word_occurrences(self.source_lines[near], word)
                    if near_occ:
                        return near, near_occ[0], near_occ[0] + len(word)
        indent = len(src_line) - len(src_line.lstrip())
        return src, indent, len(src_line.rstrip())

    def locate_name(self, src, name, neighbors=True):
        """Find identifier name on source line src (or, failing that, an adjacent line): (line, col)."""
        deltas = (0, 1, -1, 2, -2) if neighbors else (0,)
        for delta in deltas:
            near = src + delta
            if 0 <= near < len(self.source_lines):
                occ = word_occurrences(self.source_lines[near], name)
                if occ:
                    return near, occ[0]
        return None

    def compiled_indent_for(self, src_line):
        """The indentation (as a string) of the first compiled line generated from src_line."""
        lines = self.src_to_compiled.get(src_line)
        if not lines:
            return None
        text = self.compiled_line(lines[0])
        return text[:len(text) - len(text.lstrip())]


def leading_whitespace(text):
    return text[:len(text) - len(text.lstrip())]
