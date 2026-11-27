#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Compiling Coconut code and turning compiler errors/warnings into LSP diagnostics.

This module imports Coconut lazily, and is normally run inside a separate worker process
(see worker.py) so that slow compiles never block the language server, and a pathological
compile can be killed without taking the server down.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import re
import sys
import threading
import traceback

from coconut.lsp.sourcemap import CompiledDocument, word_occurrences

SEVERITY_ERROR = 1
SEVERITY_WARNING = 2
SEVERITY_INFORMATION = 3
SEVERITY_HINT = 4

TAG_UNNECESSARY = 1
TAG_DEPRECATED = 2

STRICT_HINT_RE = re.compile(r"\s*\((?:remove --pure to dismiss; )?remove --strict to downgrade to a warning\)")

DEFAULT_SETTINGS = {
    "target": "sys",
    "strict": False,
    "pure": False,
    "lint": True,
    "mypy": False,
}

# Incremental parsing reuses parse results across compiles (much faster recompiles after small
# edits), so the long-lived compile worker turns it on, for inputs below Coconut's recommended
# maximum length (it's slower for large inputs).
USE_INCREMENTAL = False

_coconut_lock = threading.Lock()
_current_setup = None


def project_settings(settings, path, explicit=()):
    """Apply the [tool.coconut] configuration in the pyproject.toml that applies to the given file.

    Settings named in explicit (set on the command line or by the editor) take precedence for
    target, and the project configuration can only turn strict and pure checks on. Returns
    (settings, diagnostics), with a diagnostic if the configuration is invalid."""
    if not path:
        return settings, []
    try:
        from coconut.project_config import find_project_config
        config = find_project_config(path)
    except Exception as err:
        return settings, [{
            "range": make_range(0, 0, 0, 0), "severity": SEVERITY_WARNING, "source": "coconut",
            "message": "ignoring invalid project configuration: " + str(err),
        }]
    if not config:
        return settings, []
    new = dict(settings)
    if "target" in config and "target" not in explicit:
        new["target"] = config["target"]
    for key in ("strict", "pure"):
        if config.get(key):
            new[key] = True
    return new, []


def coconut_info():
    """Information about the Coconut installation available to this interpreter."""
    info = {
        "python_version": ".".join(str(v) for v in sys.version_info[:3]),
        "python_executable": sys.executable,
    }
    try:
        from coconut.api import version
        info["coconut_version"] = version("num")
    except Exception as err:
        info["coconut_version"] = None
        info["coconut_error"] = "{t}: {e}".format(t=type(err).__name__, e=err)
    try:
        import pyflakes.checker  # noqa
        import pyflakes
        info["pyflakes_version"] = getattr(pyflakes, "__version__", "unknown")
    except Exception:
        info["pyflakes_version"] = None
    return info


def _set_incremental(code):
    from coconut.api import use_incremental_parsing
    from coconut.constants import disable_incremental_for_len
    try:
        use_incremental_parsing(USE_INCREMENTAL and len(code) < disable_incremental_for_len)
    except Exception:
        traceback.print_exc(file=sys.stderr)


def _setup(settings):
    global _current_setup
    from coconut.api import setup
    key = (str(settings.get("target") or "sys"), bool(settings.get("strict")), bool(settings.get("pure")))
    if key != _current_setup:
        setup(target=key[0], strict=key[1], pure=key[2], line_numbers=True, keep_lines=False, no_wrap=True, minify=False)
        _current_setup = key


def make_range(start_line, start_col, end_line, end_col):
    return {
        "start": {"line": max(start_line, 0), "character": max(start_col, 0)},
        "end": {"line": max(end_line, 0), "character": max(end_col, 0)},
    }


def _error_range(err, source_lines):
    """Compute an LSP range for a CoconutSyntaxError (or subclass) from its location."""
    from coconut.exceptions import CoconutParseError
    location = getattr(err, "location", None)
    if location is None or not source_lines:
        return make_range(0, 0, 0, len(source_lines[0]) if source_lines else 0)
    line, col, end_line, end_col = location
    if isinstance(err, CoconutParseError):
        # the location spans from the start of the failing statement to the failure point;
        # point at the failure itself
        line, col = end_line, end_col
        end_line, end_col = line, col
    last = len(source_lines) - 1
    line, end_line = max(0, min(line, last)), max(0, min(end_line, last))
    doc_line = source_lines[line]
    col = max(0, min(col, len(doc_line)))
    end_col = max(0, min(end_col, len(source_lines[end_line])))
    if (end_line, end_col) <= (line, col):
        # highlight the token at the error location (or the last character of the line)
        end_line = line
        m = re.match(r"\w+|\S", doc_line[col:])
        if m:
            end_col = col + len(m.group(0))
        elif doc_line.rstrip():
            end_col = len(doc_line.rstrip())
            col = min(col, max(end_col - 1, 0))
        else:
            end_col = col
    return make_range(line, col, end_line, end_col)


def _error_message(err):
    message = getattr(err, "bare_message", None) or str(err)
    # keep just the message itself, not any rendered snippet of the code
    return message.split("\n", 1)[0]


def _reanchor_on_quoted_name(diag, source_lines):
    """For messages like "found unused import 'os'", point the range at the name itself."""
    m = re.search(r"(?:unused import|undefined name|unused variable) '([\w.]+)'", diag["message"])
    if not m:
        return
    rng = diag["range"]
    line = rng["start"]["line"]
    if not 0 <= line < len(source_lines):
        return
    name = m.group(1).split(".")[-1]
    occ = word_occurrences(source_lines[line], name)
    if occ and not any(rng["start"]["character"] <= c < rng["end"]["character"] for c in occ):
        start = min(occ, key=lambda c: abs(c - rng["start"]["character"]))
        diag["range"] = make_range(line, start, line, start + len(name))
    if "unused" in m.group(0):
        diag["tags"] = [TAG_UNNECESSARY]


def _err_to_diagnostic(err, source_lines, severity):
    from coconut.exceptions import CoconutSyntaxError
    name = type(err).__name__
    diag = {
        "severity": severity,
        "source": "coconut",
        "code": name,
        "message": _error_message(err) if isinstance(err, CoconutSyntaxError) else str(err),
    }
    if isinstance(err, CoconutSyntaxError):
        diag["range"] = _error_range(err, source_lines)
    else:
        diag["range"] = make_range(0, 0, 0, len(source_lines[0]) if source_lines else 0)
    _reanchor_on_quoted_name(diag, source_lines)
    if "deprecated" in diag["message"].lower():
        diag["tags"] = [TAG_DEPRECATED]
    if "NOQA" in diag["message"]:
        diag["data"] = {"noqa": True}
    return diag


def compile_coconut(code, settings=None):
    """Compile code; returns {"compiled": str or None, "diagnostics": [...], "info": {...}}."""
    settings = dict(DEFAULT_SETTINGS, **(settings or {}))
    source_lines = code.splitlines()
    diagnostics = []
    compiled = None
    try:
        from coconut.api import parse
        from coconut.exceptions import CoconutException, CoconutStyleError
    except Exception as err:
        return {
            "compiled": None,
            "diagnostics": [],
            "fatal": "Coconut is not installed for {exe} ({t}: {e}); install it with: {exe} -m pip install coconut".format(
                exe=sys.executable, t=type(err).__name__, e=err,
            ),
        }

    from coconut.api import collect_warnings
    with _coconut_lock, collect_warnings() as warnings:
        try:
            try:
                _setup(settings)
                _set_incremental(code)
                compiled = parse(code, "sys")
            except CoconutStyleError as err:
                # in strict mode, report the style error as a warning and still compile normally
                diagnostics.append(_err_to_diagnostic(err, source_lines, SEVERITY_WARNING))
                _setup(dict(settings, strict=False))
                try:
                    compiled = parse(code, "sys")
                finally:
                    _setup(settings)
        except CoconutException as err:
            diagnostics.append(_err_to_diagnostic(err, source_lines, SEVERITY_ERROR))
        except RecursionError:
            diagnostics.append({
                "range": make_range(0, 0, 0, 0), "severity": SEVERITY_ERROR, "source": "coconut",
                "message": "maximum recursion depth exceeded while compiling (expression nested too deeply?)",
            })
        except Exception as err:
            diagnostics.append({
                "range": make_range(0, 0, 0, 0), "severity": SEVERITY_ERROR, "source": "coconut",
                "message": "internal Coconut compiler error: {t}: {e}".format(t=type(err).__name__, e=err),
            })
            traceback.print_exc(file=sys.stderr)

    # a --strict style error is reported once from the strict compile and again as a
    #  warning from the non-strict recompile, so dedupe ignoring --strict's hint
    def dedupe_key(diag):
        return (STRICT_HINT_RE.sub("", diag["message"]), diag["range"]["start"]["line"])
    seen = set(dedupe_key(diag) for diag in diagnostics)
    for warning in warnings:
        diag = _err_to_diagnostic(warning, source_lines, SEVERITY_WARNING)
        key = dedupe_key(diag)
        if key not in seen:
            seen.add(key)
            diagnostics.append(diag)

    if compiled is not None and settings.get("lint", True):
        try:
            covered = set()
            for diag in diagnostics:
                for name in re.findall(r"'([\w.]+)'", diag["message"]):
                    covered.add((diag["range"]["start"]["line"], name.split(".")[-1]))
            for diag in lint_compiled(code, compiled):
                names = re.findall(r"'([\w.]+)'", diag["message"])
                line = diag["range"]["start"]["line"]
                if diag["code"] in ("UndefinedName", "UnusedImport") and any((line, n.split(".")[-1]) in covered for n in names):
                    continue
                diagnostics.append(diag)
        except Exception:
            traceback.print_exc(file=sys.stderr)

    return {"compiled": compiled, "diagnostics": diagnostics}


# -----------------------------------------------------------------------------------------------------------------------
# PYFLAKES LINTING OF COMPILED CODE
# -----------------------------------------------------------------------------------------------------------------------

_star_import_names = None


def _coconut_star_names():
    global _star_import_names
    if _star_import_names is None:
        try:
            import coconut.__coconut__ as header_module
            names = getattr(header_module, "__all__", None)
            if names is None:
                names = [n for n in dir(header_module) if not n.startswith("_")]
            _star_import_names = list(names)
        except Exception:
            _star_import_names = []
    return _star_import_names


STAR_IMPORT_RE = re.compile(r"^from coconut\.__coconut__ import \*\s*$", re.MULTILINE)

# pyflakes message classes we never report, since they're artifacts of compilation
IGNORED_PYFLAKES = (
    "ImportStarUsed", "ImportStarUsage", "ImportStarNotPermitted", "FutureFeatureNotDefined",
    "LateFutureImport", "ReturnOutsideFunction", "YieldOutsideFunction",
)

PYFLAKES_SEVERITY = {
    "UndefinedName": SEVERITY_WARNING,
    "UndefinedLocal": SEVERITY_WARNING,
    "UndefinedExport": SEVERITY_WARNING,
    "UnusedImport": SEVERITY_HINT,
    "UnusedVariable": SEVERITY_HINT,
    "UnusedAnnotation": SEVERITY_HINT,
    "RedefinedWhileUnused": SEVERITY_INFORMATION,
    "ImportShadowedByLoopVar": SEVERITY_INFORMATION,
}


def _map_line_ref(doc, compiled_lineno):
    idx = compiled_lineno - 1
    src = doc.line_map[idx] if 0 <= idx < len(doc.line_map) else None
    return "line " + str(src + 1) if src is not None else "line " + str(compiled_lineno) + " of the compiled code"


def lint_compiled(source, compiled):
    """Run pyflakes (if available) over the compiled Python and map its messages back to source."""
    try:
        from pyflakes import checker
    except Exception:
        return []
    import ast

    # make the header's star import explicit so pyflakes can detect undefined names
    names = _coconut_star_names()
    explicit = "from coconut.__coconut__ import " + ", ".join(names) if names else "pass"
    checked = STAR_IMPORT_RE.sub(lambda m: explicit, compiled, count=1)
    import warnings
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # e.g. SyntaxWarnings for escapes in the compiled code
            tree = ast.parse(checked)
    except SyntaxError:
        return []
    w = checker.Checker(tree, filename="<coconut>")
    doc = CompiledDocument(source, compiled)
    diagnostics = []
    seen = set()
    for message in w.messages:
        kind = type(message).__name__
        if kind in IGNORED_PYFLAKES:
            continue
        line = message.lineno - 1
        src = doc.line_map[line] if 0 <= line < len(doc.line_map) else None
        if src is None:
            continue
        args = [a for a in getattr(message, "message_args", ()) if isinstance(a, str)]
        if any("_coconut" in a for a in args):
            continue
        text = message.message % message.message_args
        name = args[0] if args else None
        if kind == "UnusedImport" and name:
            # 'a.b.c' imported but unused -> highlight the last component
            name = name.split(" as ")[-1].split(".")[-1]
        src_line = doc.source_line(src)
        if name and not word_occurrences(src_line, name):
            # name doesn't appear in the source line: compiler-generated, so don't report it
            continue
        if kind == "RedefinedWhileUnused" and (
            re.search(r"\b(addpattern|match|case)\b", src_line)
            or (name and name.startswith("__") and name.endswith("__"))  # e.g. data types' generated methods
        ):
            continue
        if re.search(r"#.*\bnoqa\b", src_line, re.IGNORECASE):
            continue
        # pyflakes refers to other lines of the compiled code; translate them to source lines
        text = re.sub(
            r"\bline (\d+)\b",
            lambda m: _map_line_ref(doc, int(m.group(1))),
            text,
        )
        mapped = doc.compiled_to_source(line, getattr(message, "col", None), word=name)
        if mapped is None:
            continue
        sline, scol, ecol = mapped
        key = (kind, sline, scol, text)
        if key in seen:
            continue
        seen.add(key)
        diag = {
            "range": make_range(sline, scol, sline, ecol),
            "severity": PYFLAKES_SEVERITY.get(kind, SEVERITY_WARNING),
            "source": "pyflakes",
            "code": kind,
            "message": text,
        }
        if kind in ("UnusedImport", "UnusedVariable", "UnusedAnnotation"):
            diag["tags"] = [TAG_UNNECESSARY]
        diagnostics.append(diag)
    return diagnostics


# -----------------------------------------------------------------------------------------------------------------------
# ERROR-TOLERANT ANALYSIS
# -----------------------------------------------------------------------------------------------------------------------

def first_error_line(diagnostics):
    lines = [d["range"]["start"]["line"] for d in diagnostics if d.get("severity") == SEVERITY_ERROR and d.get("source") == "coconut"]
    return min(lines) if lines else None


def repair_source(text, line):
    """Neutralize source line `line` so that the rest of the file can compile for analysis.

    The line is replaced (keeping the line count) by 'pass', or by 'if True:' if it opens an
    indented block, so that the block's body stays syntactically valid."""
    lines = text.split("\n")
    if not 0 <= line < len(lines):
        return None
    current = lines[line]
    indent = current[:len(current) - len(current.lstrip())]
    next_indent = None
    for following in lines[line + 1:]:
        if following.strip() and not following.strip().startswith("#"):
            next_indent = len(following) - len(following.lstrip())
            break
    if next_indent is not None and next_indent > len(indent):
        replacement = indent + "if True:"
    else:
        replacement = indent + "pass"
    if replacement == current:
        return None
    lines[line] = replacement
    return "\n".join(lines)
