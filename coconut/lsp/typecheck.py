#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Optional mypy type checking of the compiled Python, mapped back to the Coconut source.

The compiled document is written into the workspace mirror (see overlay.py), next to compiled
versions of the Coconut modules it imports, and mypy checks it there.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import re
import subprocess
import sys

from coconut.lsp.compiler import SEVERITY_ERROR, SEVERITY_INFORMATION, make_range
from coconut.lsp.sourcemap import CompiledDocument

MYPY_LINE_RE = re.compile(r"^(?P<path>.+?):(?P<line>\d+):(?:(?P<col>\d+):)? (?P<sev>error|note|warning): (?P<msg>.*?)(?:  \[(?P<code>[\w-]+)\])?$")
_running = set()


def kill_running():
    """Kill any mypy processes still running (e.g. when the server exits)."""
    for proc in list(_running):
        try:
            proc.kill()
        except Exception:
            pass


CONFIG_FILES = ("mypy.ini", ".mypy.ini", "pyproject.toml", "setup.cfg")


def mypy_available(python=None):
    try:
        import importlib.util
        return importlib.util.find_spec("mypy") is not None
    except Exception:
        return False


def find_config(root):
    for name in CONFIG_FILES:
        path = os.path.join(root, name)
        if os.path.isfile(path):
            if name in ("pyproject.toml", "setup.cfg"):
                try:
                    with open(path, encoding="utf-8") as f:
                        if "mypy" not in f.read():
                            continue
                except (OSError, UnicodeDecodeError):
                    continue
            return path
    return None


def run_mypy(doc_path, source, compiled, overlay, roots, timeout=300, extra_args=()):
    """Type-check compiled code; returns a list of LSP diagnostics for the Coconut source."""
    root = overlay.root_for(doc_path, roots)
    mirror_root = overlay.mirror_root(root)
    target = overlay.script_path(doc_path, roots)
    overlay.prepare(doc_path, source, roots)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(compiled)
    args = [
        sys.executable, "-m", "mypy",
        "--show-column-numbers", "--show-error-codes", "--no-error-summary", "--no-pretty",
        "--hide-error-context", "--no-color-output", "--follow-imports=silent",
        # one cache shared by all projects: the expensive part (the standard library) is reused,
        # and mypy still validates each cached module against its source
        "--cache-dir", os.path.join(overlay.base_dir, ".mypy_cache"),
    ]
    config = find_config(root)
    if config:
        args += ["--config-file", config]
    args += list(extra_args) + [target]
    env = dict(os.environ)
    env["MYPYPATH"] = mirror_root + (os.pathsep + root)
    # stdin must not be inherited: in the language server it's the LSP pipe from the editor
    proc = subprocess.Popen(
        args, cwd=mirror_root, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    _running.add(proc)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        sys.stderr.write("mypy timed out after {t} seconds\n".format(t=timeout))
        return []
    finally:
        _running.discard(proc)
    diagnostics = parse_mypy_output(out, target, source, compiled, cwd=mirror_root)
    if not diagnostics and proc.returncode == 1:
        sys.stderr.write("mypy reported errors, but none could be mapped to {t}:\n{o}\n".format(t=target, o=out[-2000:]))
    if proc.returncode not in (0, 1):
        # mypy itself failed (bad config, crash, ...): say why rather than silently reporting nothing
        sys.stderr.write("mypy exited with code {c}:\n{o}\n{e}\n".format(c=proc.returncode, o=out[-2000:], e=err[-2000:]))
    return diagnostics


def _canonical(path):
    """Comparable form of a path (resolves symlinks and, on Windows, 8.3 short names and case)."""
    try:
        path = os.path.realpath(path)
    except (OSError, ValueError):
        path = os.path.abspath(path)
    return os.path.normcase(path)


def parse_mypy_output(output, target, source, compiled, cwd=None):
    doc = CompiledDocument(source, compiled)
    target_norm = _canonical(target)
    diagnostics = []
    seen = set()
    for line in output.splitlines():
        m = MYPY_LINE_RE.match(line.strip())
        if not m:
            continue
        path = m.group("path")
        if cwd is not None and not os.path.isabs(path):
            path = os.path.join(cwd, path)
        if _canonical(path) != target_norm:
            continue
        message = m.group("msg")
        if "_coconut" in message or "__coconut__" in message:
            continue
        cline = int(m.group("line")) - 1
        col = int(m.group("col")) - 1 if m.group("col") else None
        mapped = doc.compiled_to_source(cline, col)
        if mapped is None:
            continue
        sline, scol, ecol = mapped
        key = (sline, scol, message)
        if key in seen:
            continue
        seen.add(key)
        diag = {
            "range": make_range(sline, scol, sline, ecol),
            "severity": SEVERITY_ERROR if m.group("sev") == "error" else SEVERITY_INFORMATION,
            "source": "mypy",
            "message": message,
        }
        if m.group("code"):
            diag["code"] = m.group("code")
        diagnostics.append(diag)
    return diagnostics
