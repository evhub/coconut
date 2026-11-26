#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Editor-independent analysis of Coconut code for the Coconut language server.

Positions here are 0-indexed (line, character) pairs, matching the Language Server Protocol.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import re
import difflib
import threading
from contextlib import contextmanager

from coconut.terminal import logger
from coconut.exceptions import (
    CoconutException,
    CoconutSyntaxError,
)
from coconut.compiler import Compiler
from coconut.compiler.util import extract_line_num_from_comment

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

identifier_regex = re.compile(r"[A-Za-z_]\w*")
trailing_dotted_name_regex = re.compile(r"(?:[A-Za-z_]\w*\.)*[A-Za-z_]?\w*$")
symbol_regexes = (
    # (regex, kind)
    (re.compile(r"^(\s*)(?:(?:async|match|addpattern|case|copyclosure|yield)\s+)*def\s+([A-Za-z_][\w.]*)"), "function"),
    (re.compile(r"^(\s*)class\s+([A-Za-z_]\w*)"), "class"),
    (re.compile(r"^(\s*)(?:match\s+)?data\s+([A-Za-z_]\w*)"), "class"),
    (re.compile(r"^(\s*)type\s+([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*="), "type"),
    (re.compile(r"^(\s*)operator\s+(\S+)"), "operator"),
)

coconut_keywords = (
    "data", "match", "case", "cases", "where", "addpattern", "operator", "then",
    "copyclosure", "lazy", "final", "def", "class", "async", "await", "yield",
    "return", "if", "elif", "else", "for", "while", "try", "except", "finally",
    "with", "import", "from", "as", "in", "not", "and", "or", "is", "lambda",
    "pass", "break", "continue", "raise", "del", "global", "nonlocal", "assert",
    "True", "False", "None",
)

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def word_at(line, character):
    """Get the identifier at the given character in line, along with its start and end."""
    for match in identifier_regex.finditer(line):
        if match.start() <= character <= match.end():
            return match.group(), match.start(), match.end()
    return None, None, None


def nth_word_occurrence(line, word, start):
    """Get which occurrence of word in line the occurrence beginning at start is."""
    n = 0
    for match in re.finditer(r"\b" + re.escape(word) + r"\b", line):
        if match.start() >= start:
            return n
        n += 1
    return n


def find_word_occurrences(line, word):
    """Find the starting indices of all whole-word occurrences of word in line, ignoring comments."""
    code = line.split("#", 1)[0]
    return [match.start() for match in re.finditer(r"\b" + re.escape(word) + r"\b", code)]


def leading_whitespace(line):
    """Get the leading whitespace of line."""
    return line[:len(line) - len(line.lstrip())]


@contextmanager
def capturing_warnings():
    """Capture all warnings issued through the Coconut logger."""
    warnings = []
    old_warn_err = logger.warn_err

    def warn_err(warning, force=False):
        warnings.append(warning)
    logger.warn_err = warn_err
    try:
        yield warnings
    finally:
        logger.warn_err = old_warn_err


# -----------------------------------------------------------------------------------------------------------------------
# DIAGNOSTICS:
# -----------------------------------------------------------------------------------------------------------------------


class Diagnostic(object):
    """An editor-independent diagnostic."""
    __slots__ = ("start", "end", "message", "severity")

    def __init__(self, start, end, message, severity):
        self.start = start
        self.end = end
        self.message = message
        self.severity = severity

    def __repr__(self):
        return "Diagnostic({start!r}, {end!r}, {message!r}, {severity!r})".format(
            start=self.start,
            end=self.end,
            message=self.message,
            severity=self.severity,
        )


def error_to_diagnostic(err, source_lines, severity):
    """Convert a CoconutSyntaxError into a Diagnostic."""
    kwargs = err.kwargs
    message = kwargs["message"] or "parsing failed"
    if kwargs.get("extra"):
        message += " (" + str(kwargs["extra"]) + ")"
    ln = kwargs.get("ln")
    snippet = kwargs.get("source") or ""
    point = kwargs.get("point") or 0
    endpoint = kwargs.get("endpoint")

    num_lines = max(len(source_lines), 1)
    line_ind = min(max((ln or 1) - 1, 0), num_lines - 1)
    doc_line = source_lines[line_ind] if source_lines else ""

    # the snippet may have been reformatted (e.g. reindented), so convert
    #  the point into a column in the actual line by correcting for indentation
    snippet_lines = snippet.split("\n")
    first_snip_line = snippet_lines[0]
    snip_indent = len(leading_whitespace(first_snip_line))
    doc_indent = len(leading_whitespace(doc_line))
    start_char = min(max(doc_indent + (point - snip_indent), doc_indent), len(doc_line))

    end_line_ind, end_char = line_ind, len(doc_line)
    if endpoint is not None and endpoint > point:
        before_end = snippet[:endpoint]
        extra_lines = before_end.count("\n")
        end_line_ind = min(line_ind + extra_lines, num_lines - 1)
        end_doc_line = source_lines[end_line_ind] if source_lines else ""
        if extra_lines:
            last_snip_line = before_end.rsplit("\n", 1)[1]
            end_char = len(leading_whitespace(end_doc_line)) + len(last_snip_line.lstrip())
        else:
            end_char = doc_indent + (endpoint - snip_indent)
        end_char = min(max(end_char, 0), len(end_doc_line))
    if (end_line_ind, end_char) <= (line_ind, start_char):
        # highlight at least the rest of the line
        end_line_ind, end_char = line_ind, max(len(doc_line), start_char + 1)
    return Diagnostic((line_ind, start_char), (end_line_ind, end_char), message, severity)


# -----------------------------------------------------------------------------------------------------------------------
# ANALYSIS:
# -----------------------------------------------------------------------------------------------------------------------


class CompiledDocument(object):
    """The result of successfully compiling a Coconut document."""

    def __init__(self, source, compiled, path=None):
        self.source = source
        self.source_lines = source.splitlines()
        self.compiled = compiled
        self.compiled_lines = compiled.splitlines()
        self.path = path

        # maps between compiled line indices and Coconut line indices
        self.coconut_line_for = {}
        self.compiled_lines_for = {}
        for compiled_ind, compiled_line in enumerate(self.compiled_lines):
            ln = extract_line_num_from_comment(compiled_line)
            if ln is not None:
                coconut_ind = ln - 1
                self.coconut_line_for[compiled_ind] = coconut_ind
                self.compiled_lines_for.setdefault(coconut_ind, []).append(compiled_ind)

        self._script = None

    @property
    def script(self):
        """Get a jedi Script for the compiled code."""
        if self._script is None:
            import jedi
            self._script = jedi.Script(self.compiled, path=self.jedi_path)
        return self._script

    @property
    def jedi_path(self):
        """The path to tell jedi the compiled code is at."""
        if self.path is None:
            return None
        base, ext = self.path.rsplit(".", 1) if "." in self.path else (self.path, "")
        return base + ".py"

    def compiled_position(self, line, character):
        """Find the position in the compiled code corresponding to the identifier at the given position."""
        if line >= len(self.source_lines):
            return None, None
        source_line = self.source_lines[line]
        word, start, _ = word_at(source_line, character)
        if word is None:
            return None, None
        occurrence = nth_word_occurrence(source_line, word, start)
        candidates = []
        for compiled_ind in self.compiled_lines_for.get(line, ()):
            for col in find_word_occurrences(self.compiled_lines[compiled_ind], word):
                candidates.append((compiled_ind, col))
        if not candidates:
            return word, None
        return word, candidates[min(occurrence, len(candidates) - 1)]

    def coconut_position(self, compiled_line, compiled_col, name=None):
        """Map a position in the compiled code back to the Coconut source."""
        coconut_ind = self.coconut_line_for.get(compiled_line)
        if coconut_ind is None or coconut_ind >= len(self.source_lines):
            return None
        source_line = self.source_lines[coconut_ind]
        col = 0
        if name is not None:
            occurrences = find_word_occurrences(source_line, name)
            if occurrences:
                col = occurrences[0]
        else:
            col = len(leading_whitespace(source_line))
        return (coconut_ind, col)

    def hover(self, line, character):
        """Get hover text for the given position, or None."""
        word, compiled_pos = self.compiled_position(line, character)
        if compiled_pos is None:
            return None
        compiled_ind, col = compiled_pos
        try:
            names = self.script.help(compiled_ind + 1, col)
            if not names:
                names = self.script.infer(compiled_ind + 1, col)
        except Exception:
            logger.log_exc()
            return None
        parts = []
        for name in names[:3]:
            try:
                header = name.description
                if name.type in ("function", "class") or name.type == "instance":
                    sigs = name.get_signatures()
                    if sigs:
                        header = "\n".join(sig.to_string() for sig in sigs)
                docstring = name.docstring(raw=True)
            except Exception:
                logger.log_exc()
                continue
            part = "```python\n" + header + "\n```"
            if docstring:
                part += "\n\n" + docstring
            parts.append(part)
        if not parts:
            return None
        # clean up references to Coconut internals
        return "\n\n---\n\n".join(parts).replace("_coconut.typing.", "typing.")

    def definitions(self, line, character):
        """Get the definition locations of the name at the given position as (path, line, character) tuples.

        A path of None means the definition is in this document."""
        word, compiled_pos = self.compiled_position(line, character)
        if compiled_pos is None:
            return []
        compiled_ind, col = compiled_pos
        try:
            names = self.script.goto(compiled_ind + 1, col, follow_imports=True)
        except Exception:
            logger.log_exc()
            return []
        locations = []
        for name in names:
            if name.line is None:
                continue
            module_path = str(name.module_path) if name.module_path is not None else None
            if module_path is None or (self.jedi_path is not None and module_path == self.jedi_path) or name.module_path is None:
                coconut_pos = self.coconut_position(name.line - 1, name.column, name.name)
                if coconut_pos is not None:
                    locations.append((None,) + coconut_pos)
            else:
                locations.append(map_compiled_file_location(module_path, name.line - 1, name.column, name.name))
        return locations

    def completions(self, current_source, line, character):
        """Get completions as (name, kind, description) tuples for the given position in current_source.

        current_source may differ from the source this document was compiled from (e.g. if the user
        is in the middle of typing), so positions are mapped using a diff of the two sources."""
        current_lines = current_source.splitlines()
        if line >= len(current_lines):
            return []
        prefix_text = current_lines[line][:character]
        prefix = trailing_dotted_name_regex.search(prefix_text).group()

        # find where the current line is in the compiled source
        old_line = map_line_through_diff(current_lines, self.source_lines, line)
        insert_at, indent = self.insertion_point(old_line)
        if insert_at is None:
            return keyword_completions(prefix)

        # insert a synthetic line with the prefix at the right place and complete there
        new_compiled_lines = list(self.compiled_lines)
        new_compiled_lines.insert(insert_at, indent + prefix)
        try:
            import jedi
            completions = jedi.Script("\n".join(new_compiled_lines), path=self.jedi_path).complete(insert_at + 1, len(indent) + len(prefix))
        except Exception:
            logger.log_exc()
            return keyword_completions(prefix)
        results = []
        seen = set()
        for comp in completions:
            if comp.name.startswith("_coconut") or comp.name in seen:
                continue
            seen.add(comp.name)
            results.append((comp.name, comp.type, comp.description))
        if "." not in prefix:
            for name, kind, desc in keyword_completions(prefix):
                if name not in seen:
                    results.append((name, kind, desc))
        return results

    def insertion_point(self, old_line):
        """Find where to insert a synthetic line in the compiled code to be in the same scope as old_line.

        Returns (compiled line index to insert at, indentation)."""
        if old_line is None:
            return None, None
        # insert right before the first compiled line for this Coconut line, or after the last
        #  compiled line for the closest previous Coconut line
        for coconut_ind in range(old_line, -1, -1):
            compiled_inds = self.compiled_lines_for.get(coconut_ind)
            if compiled_inds:
                if coconut_ind == old_line:
                    insert_at = compiled_inds[0]
                    indent = leading_whitespace(self.compiled_lines[insert_at])
                else:
                    insert_at = compiled_inds[-1] + 1
                    prev_line = self.compiled_lines[compiled_inds[-1]]
                    indent = leading_whitespace(prev_line)
                    if prev_line.split("#", 1)[0].rstrip().endswith(":"):
                        indent += "    "
                return insert_at, indent
        return None, None


def keyword_completions(prefix):
    """Get completions for Coconut keywords matching prefix."""
    if "." in prefix:
        return []
    return [(kwd, "keyword", "keyword") for kwd in coconut_keywords if kwd.startswith(prefix)]


def map_line_through_diff(new_lines, old_lines, new_line):
    """Map a line index in new_lines to the corresponding line index in old_lines."""
    if new_lines == old_lines:
        return new_line
    matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if new_start <= new_line < new_end:
            if tag == "equal":
                return old_start + (new_line - new_start)
            # for changed lines, use the corresponding old line if there is one
            return min(old_start + (new_line - new_start), max(old_end - 1, old_start))
    return len(old_lines) - 1 if old_lines else None


compiled_from_regex = re.compile(r"^# This file was compiled from (.+?) by the Coconut compiler")


def map_compiled_file_location(module_path, line, column, name):
    """If module_path is a compiled Coconut file, map the given location back to its Coconut source."""
    import os
    try:
        with open(module_path) as compiled_file:
            compiled_lines = compiled_file.read().splitlines()
    except (IOError, OSError):
        return (module_path, line, column)
    source_name = None
    for header_line in compiled_lines[:10]:
        match = compiled_from_regex.match(header_line)
        if match:
            source_name = match.group(1)
            break
    if source_name is None or line >= len(compiled_lines):
        return (module_path, line, column)
    source_path = os.path.join(os.path.dirname(module_path), source_name)
    if not os.path.exists(source_path):
        # the compiled file might be in a __coconut_cache__ directory
        source_path = os.path.join(os.path.dirname(os.path.dirname(module_path)), source_name)
    ln = extract_line_num_from_comment(compiled_lines[line])
    if ln is None or not os.path.exists(source_path):
        return (module_path, line, column)
    col = 0
    try:
        with open(source_path) as source_file:
            source_lines = source_file.read().splitlines()
        if ln - 1 < len(source_lines):
            occurrences = find_word_occurrences(source_lines[ln - 1], name)
            col = occurrences[0] if occurrences else 0
    except (IOError, OSError):
        pass
    return (source_path, ln - 1, col)


def document_symbols(source):
    """Get the symbols defined in the given Coconut source as (name, kind, line, character, indent level) tuples.

    This works directly on the source, so it works even when the source fails to compile."""
    symbols = []
    for line_ind, line in enumerate(source.splitlines()):
        for regex, kind in symbol_regexes:
            match = regex.match(line)
            if match:
                symbols.append((match.group(2), kind, line_ind, match.start(2), len(match.group(1))))
                break
    return symbols


class Analyzer(object):
    """Compiles Coconut documents and keeps track of the most recent successful compilation of each."""

    def __init__(self, target="sys", **compiler_kwargs):
        self.compiler = Compiler(target=target, line_numbers=True, **compiler_kwargs)
        self.lock = threading.Lock()
        self.last_good = {}  # uri -> CompiledDocument
        self.warmed_up = False

    def warm_up(self):
        """Warm up the compiler (this can take a little while)."""
        with self.lock:
            if not self.warmed_up:
                self.compiler.warm_up(enable_incremental_mode=True)
                self.warmed_up = True

    def analyze(self, uri, source, path=None):
        """Compile the given source and return a list of Diagnostics."""
        self.warm_up()
        source_lines = source.splitlines()
        diagnostics = []
        with self.lock:
            with capturing_warnings() as warnings:
                try:
                    compiled = self.compiler.parse_sys(source, codepath=path, use_cache=False)
                except CoconutSyntaxError as err:
                    diagnostics.append(error_to_diagnostic(err, source_lines, "error"))
                    compiled = None
                except CoconutException as err:
                    diagnostics.append(Diagnostic((0, 0), (0, 1), str(err), "error"))
                    compiled = None
        for warning in warnings:
            if isinstance(warning, CoconutSyntaxError):
                diagnostics.append(error_to_diagnostic(warning, source_lines, "warning"))
        if compiled is not None:
            self.last_good[uri] = CompiledDocument(source, compiled, path)
        return diagnostics

    def get_compiled(self, uri):
        """Get the most recent successfully compiled version of the given document, or None."""
        return self.last_good.get(uri)

    def forget(self, uri):
        """Forget about the given document."""
        self.last_good.pop(uri, None)
